from uwsgiconf.config import configure_uwsgi
from uwsgiconf.presets.nice import PythonSection


def get_configurations():

    from django.conf import settings

    in_production = settings.IN_PRODUCTION

    project = settings.PROJECT_NAME
    domain = settings.PROJECT_DOMAIN

    dir_state = settings.PROJECT_DIR_STATE
    dir_spool = dir_state / 'spool'
    dir_runtime = settings.PROJECT_DIR_RUNTIME

    section = PythonSection.bootstrap(
        'http://:%s' % (80 if in_production else 8000),
        allow_shared_sockets=False,

        wsgi_module='%s.wsgi' % project,
        process_prefix='[%s] ' % project,

        log_dedicated=True,
        ignore_write_errors=True,
        touch_reload=str(dir_state / 'reloader'),
    )
    section.set_runtime_dir(str(dir_runtime.parent))
    section.main_process.change_dir(str(dir_state))

    if dir_spool.exists():
        section.spooler.add(str(dir_spool))

    if in_production and domain:
        webroot = str(dir_state / 'certbot')
        section.configure_certbot_https(domain=domain, webroot=webroot, allow_shared_sockets=False)

    section.configure_maintenance_mode(
        str(dir_state / 'maintenance'), section.get_bundled_static_path('503.html'))

    return section


configure_uwsgi(get_configurations)

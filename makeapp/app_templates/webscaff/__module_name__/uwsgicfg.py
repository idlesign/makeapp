from uwsgiconf.config import configure_uwsgi
from uwsgiconf.presets.nice import PythonSection


def get_configurations():

    from django.conf import settings

    in_production = settings.IN_PRODUCTION

    project = settings.PROJECT_NAME
    domain = settings.PROJECT_DOMAIN

    dir_project = settings.PROJECT_DIR_ROOT
    dir_runtime = settings.PROJECT_DIR_RUNTIME

    section = PythonSection.bootstrap(
        'http://:%s' % (80 if in_production else 8000),

        wsgi_module='%s.wsgi' % project,
        process_prefix='[%s] ' % project,

        log_dedicated=True,
        ignore_write_errors=True,
        touch_reload=str(dir_runtime / 'reloader'),
        owner=project if in_production else None,
    )

    section.main_process.change_dir(str(dir_project))

    section.spooler.add(str(dir_runtime / 'spool'))

    if in_production and domain:
        webroot = str(dir_runtime / 'certbot')
        section.configure_certbot_https(domain=domain, webroot=webroot)

    section.configure_maintenance_mode(
        str(dir_runtime / 'maintenance'), section.get_bundled_static_path('503.html'))

    return section


configure_uwsgi(get_configurations)

from pathlib import Path

from envbox import get_environment
from uwsgiconf.config import configure_uwsgi
from uwsgiconf.presets.nice import PythonSection


def get_configurations():

    project = '{{ module_name }}'
    domain = '{{ webscaff_domain }}'

    dir_runtime = Path('../runtime/').absolute()

    environ = get_environment()

    developer_mode = environ.is_development

    section = PythonSection.bootstrap(
        'http://:%s' % 8000 if developer_mode else 80,

        wsgi_module='%s.wsgi' % project,
        process_prefix='[%s] ' % project,

        log_dedicated=True,
        ignore_write_errors=True,
        touch_reload=str(dir_runtime / 'reloader'),
        owner=project if developer_mode else None,
    )

    section.spooler.add(str(dir_runtime / 'spool'))

    if not developer_mode and domain:
        webroot = str(dir_runtime / 'certbot')
        section.configure_certbot_https(domain=domain, webroot=webroot)

    section.configure_maintenance_mode(
        str(dir_runtime / 'maintenance'), section.get_bundled_static_path('503.html'))

    return section


configure_uwsgi(get_configurations)

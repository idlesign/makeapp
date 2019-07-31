from uwsgiconf.config import configure_uwsgi


def get_configurations():

    from pathlib import Path
    from envbox import get_environment
    from uwsgiconf.presets.nice import PythonSection

    section = PythonSection(

        wsgi_module='%s' % (Path(__file__).absolute().parent / 'wsgi.py'),
        log_dedicated=True,
        ignore_write_errors=True,
        owner='{{ module_name }}',
        process_prefix='{{ module_name }}',

    )
    networking = section.networking

    sockets = [
        networking.sockets.http(':80'),
    ]

    environ = get_environment()
    settings = environ.getmany('{{ module_name }}_HTTPS_'.upper())

    https_cert = settings.get('CERT')
    https_key = settings.get('KEY')

    if https_cert and https_key:
        sockets.append(
            networking.sockets.https(':443', cert=https_cert, key=https_key)
        )

    networking.register_socket(sockets)

    return section


configure_uwsgi(get_configurations)

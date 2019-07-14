from uwsgiconf.config import configure_uwsgi


def get_configurations():

    from os.path import dirname, abspath, join
    from uwsgiconf.presets.nice import PythonSection

    section = PythonSection(
        wsgi_module=join(dirname(abspath(__file__)), 'wsgi.py')

    ).networking.register_socket(
        PythonSection.networking.sockets.http(':80')
    )

    return section


configure_uwsgi(get_configurations)

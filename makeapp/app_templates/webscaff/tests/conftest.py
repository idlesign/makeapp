import os

from pytest_djangoapp import configure_djangoapp_plugin

# Use mock for uwsgi.
os.environ['UWSGICONF_FORCE_STUB'] = '1'

pytest_plugins = configure_djangoapp_plugin(
    settings='{{ module_name }}.settings.settings_testing',
    admin_contrib=True,
    migrate=False,
)

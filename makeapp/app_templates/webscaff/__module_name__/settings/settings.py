"""
Configuration entry point.

import_by_environment() will add into current namespace symbols
from settings_X.py module appropriate for the current environment --
for example for development environment it'll load symbols from `settings_development.py`.

"""
from envbox import import_by_environment, get_environment


current_env = import_by_environment(
    # For production one can place `../conf/environment` file with `production` as it contents.
    get_environment(detectors_opts={'file': {'source': '../conf/environment'}}))


IN_PRODUCTION = current_env == 'production'

print('# Environment type: %s' % current_env)

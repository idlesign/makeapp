"""
Configuration entry point.

import_by_environment() will add into current namespace symbols
from settings_X.py module appropriate for the current environment --
for example for development environment it'll load symbols from `settings_development.py`.

"""
from pathlib import Path

from envbox import import_by_environment, get_environment


PROJECT_NAME = '{{ module_name }}'
PROJECT_DOMAIN = '{{ webscaff_domain }}'
PROJECT_DIR_ROOT = Path('/srv') / PROJECT_NAME
PROJECT_DIR_RUNTIME = PROJECT_DIR_ROOT / 'runtime'


current_env = import_by_environment(
    # For production one can place `../runtime/environment` file with `production` as it contents.
    get_environment(detectors_opts={'file': {'source': str(PROJECT_DIR_RUNTIME / 'environ')}}))


IN_PRODUCTION = current_env == 'production'

print('# Environment type: %s' % current_env)

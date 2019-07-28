# This will be used as Django settings file in production environment.
from .settings_base import *


DEBUG = False


ALLOWED_HOSTS = [
    # Don't forget to put here all IPs and
    # domain names your is service available at.
    '{{ webscaff_host }}',
]

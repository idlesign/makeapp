# This will be used as Django settings file in production environment.
from .base import *


DEBUG = False


ALLOWED_HOSTS = [
    # Don't forget to put here all IPs and
    # domain names your is service available at.
    '{{ webscaff_host }}',
{% if webscaff_domain %}
    PROJECT_DOMAIN,
{% endif %}

]

{% if webscaff_email %}
ADMINS = (
    ('Administrator', '{{ webscaff_email }}'),
)
{% endif %}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': PROJECT_NAME,
        'USER': PROJECT_NAME,
        # We'll use Unix domain sockets, so we omit PASSWORD, HOST, PORT
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': f'{PROJECT_DIR_CACHE}',
    }
}

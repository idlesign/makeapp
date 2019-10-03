# This will be used as Django settings file in production environment.
from .settings_base import *


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
        'PASSWORD': '{{ webscaff_db_password }}',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


STATIC_ROOT = str(PROJECT_DIR_RUNTIME / 'static')
MEDIA_ROOT = str(PROJECT_DIR_RUNTIME / 'media')

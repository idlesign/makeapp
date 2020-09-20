from .base import *  # noqa


DEBUG = True


ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '[::1]',
]

INTERNAL_IPS = [
    '127.0.0.1',
    '[::1]',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': f'{PROJECT_DIR_STATE}/data.db',
    }
}

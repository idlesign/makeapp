from .settings_base import *


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

ADMINS = (
    ('me', 'me@some.where'),
)

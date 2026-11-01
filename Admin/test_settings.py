'''
Isolated settings for custom-admin tests; never uses the application database
'''
from core.settings import *  # noqa: F401,F403

DATABASES = {
    'default':
        {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    }

CACHES = {
    'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
            }
        }

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.InMemoryStorage'\
        },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'
        },
}

ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

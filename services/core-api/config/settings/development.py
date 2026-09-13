from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'staymatch_db'),
        'USER': os.getenv('POSTGRES_USER', 'staymatch_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'staymatch_password'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# Fallback to SQLite for standalone local python manage.py test without PostgreSQL running
if os.getenv('USE_SQLITE_DEV', 'False') == 'True':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

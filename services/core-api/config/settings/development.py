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

# Development Redis cache check & fallback
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
try:
    import redis
    r = redis.Redis.from_url(REDIS_URL, socket_connect_timeout=1)
    r.ping()
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'KEY_PREFIX': 'staymatch',
            'TIMEOUT': 300,
        }
    }

except Exception:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'staymatch-dev-fallback',
        }
    }


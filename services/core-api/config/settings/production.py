from django.core.exceptions import ImproperlyConfigured

from .base import *
import os

DEBUG = False


def _required_secret_key():
    key = os.getenv('SECRET_KEY', '')
    if len(key) < 32 or key.startswith('django-insecure'):
        raise ImproperlyConfigured(
            'SECRET_KEY must be set to a unique random value of at least 32 characters in production.')
    return key


SECRET_KEY = _required_secret_key()

ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h.strip()]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured('ALLOWED_HOSTS must list the host names this site is served from.')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'staymatch_db'),
        'USER': os.getenv('POSTGRES_USER', 'staymatch_user'),
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.getenv('POSTGRES_HOST', 'postgres'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': 600,
    }
}

# Static files compression and caching with WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Behind nginx: trust its X-Forwarded-Proto, and count it as the one proxy for client addresses.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
REST_FRAMEWORK = {**REST_FRAMEWORK, 'NUM_PROXIES': int(os.getenv('NUM_PROXIES', '1'))}

# Security headers and cookie flags
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'  # nginx redirects http to https
SESSION_COOKIE_SECURE = True
REFRESH_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

# Cross-origin access is off unless origins are listed. The browser app is served from the same origin as the
# API (through nginx), so it needs none.
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [o.strip() for o in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]

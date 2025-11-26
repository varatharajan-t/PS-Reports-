"""
Production settings for SAP Project System Reports
Import from settings.py and override for production environment
"""

from .settings import *
from decouple import config as env_config

# SECURITY SETTINGS - CRITICAL FOR PRODUCTION
DEBUG = False

# SECRET_KEY must be set in environment variable
SECRET_KEY = env_config('SECRET_KEY')

# ALLOWED_HOSTS must be properly configured
ALLOWED_HOSTS = env_config('ALLOWED_HOSTS').split(',')

# Security middleware settings
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Database - Consider PostgreSQL for production
# Uncomment and configure if using PostgreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': env_config('DB_NAME'),
#         'USER': env_config('DB_USER'),
#         'PASSWORD': env_config('DB_PASSWORD'),
#         'HOST': env_config('DB_HOST', default='localhost'),
#         'PORT': env_config('DB_PORT', default='5432'),
#         'CONN_MAX_AGE': 600,
#     }
# }

# Static files - Use WhiteNoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging - More detailed logging for production
LOGGING['handlers']['file']['level'] = 'WARNING'
LOGGING['handlers']['error_file']['level'] = 'ERROR'
LOGGING['loggers']['django']['level'] = 'WARNING'

# Email configuration (for error notifications)
if env_config('EMAIL_HOST', default=None):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env_config('EMAIL_HOST')
    EMAIL_PORT = env_config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = env_config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = env_config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = env_config('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = env_config('DEFAULT_FROM_EMAIL', default='noreply@example.com')

    # Send error emails to admins
    ADMINS = [
        ('Admin', env_config('ADMIN_EMAIL', default='admin@example.com')),
    ]
    MANAGERS = ADMINS

# Cache configuration (optional - use Redis for production)
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': env_config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
#     }
# }

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = False

# File upload limits (stricter in production)
FILE_UPLOAD_MAX_MEMORY_SIZE = env_config('MAX_UPLOAD_SIZE', default=52428800, cast=int)  # 50MB
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE

# Celery configuration (if using async processing)
# CELERY_BROKER_URL = env_config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
# CELERY_RESULT_BACKEND = env_config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = TIME_ZONE

# Error tracking (Sentry)
# if env_config('SENTRY_DSN', default=None):
#     import sentry_sdk
#     from sentry_sdk.integrations.django import DjangoIntegration
#
#     sentry_sdk.init(
#         dsn=env_config('SENTRY_DSN'),
#         integrations=[DjangoIntegration()],
#         traces_sample_rate=0.1,
#         send_default_pii=False,
#         environment='production',
#     )

# Compress and optimize static files
STATICFILES_FINDERS.append('django.contrib.staticfiles.finders.DefaultStorageFinder')

print("⚠️  Production settings loaded - DEBUG is OFF")

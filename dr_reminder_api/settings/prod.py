from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
LOGGING = {
  "version": 1,
  "handlers": {"console": {"class": "logging.StreamHandler"}},
  "loggers": {"django.request": {"handlers": ["console"], "level": "ERROR"}},
}
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,0.0.0.0,web"
).split(",")
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8002",
    "http://127.0.0.1:8002",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
DIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": int(os.environ["POSTGRES_PORT"]),
    }
}
print("DATABASES:", DATABASES)

"""
Django settings for moments project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Custom Attributes
VALID_IMAGE_EXTS       = [".PNG", ".JPG", ".JPEG"]
TMP_PATH               = '/tmp/'
MEDIA_ROOT             = os.path.join(BASE_DIR,'moments/static/assets/')
MOMENT_UPLOAD_PATH     = 'moments'
PROJECT_BASE           = os.path.join(BASE_DIR,'moments/static')
COMPRESS_ROOT          = os.path.join(BASE_DIR,'moments/static/')
MOMENT_API_THUMB_WIDTH = 304   # Pixels
ONE_DAY                = 86400 # Seconds

CACHE_CONTROL = (
    ("api/",                        {"max_age" : ONE_DAY, "s_maxage" : ONE_DAY, "public" : True}),
    ("\.(gif|jpg|png|GIF|PNG|JPG)", {"max_age" : ONE_DAY, "s_maxage" : ONE_DAY, "public" : True}),
)

REVERSE_PROXY_RULES = (
    ("api/",        ONE_DAY, "application/json"),
    ("\.(jpg|JPG)", ONE_DAY, "image/jpeg"),
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'local-cache'
    }
}



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG            = False
TEMPLATE_DEBUG   = DEBUG
COMPRESS_ENABLED = not DEBUG
ALLOWED_HOSTS    = ["*"]

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'south',
    'tastypie',
    'taggit',
    'moments.apps.base',
    'compressor',
    'adminsortable',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'moments.middleware.proxy.CacheControlProxy',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'moments.middleware.proxy.ReverseProxy',
)

ROOT_URLCONF     = 'moments.urls'
WSGI_APPLICATION = 'moments.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE'   : 'django.db.backends.mysql',
        'NAME'     : 'moments',
        'USER'     : '',
        'PASSWORD' : '',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,'moments/templates/'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

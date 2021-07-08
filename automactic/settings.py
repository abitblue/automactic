"""
Django settings for automactic project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os

import logging.config
import logging.handlers
from django.utils.log import DEFAULT_LOGGING


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
assert(os.environ.get('AMAC_SECRET_KEY') is not None, 'Environment variable "AMAC_SECRET_KEY" not defined')
SECRET_KEY = os.environ.get('AMAC_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (os.environ.get('AMAC_DEBUG', '') == 'True')

ALLOWED_HOSTS_PRE = os.environ.get("AMAC_ALLOWED_HOSTS", "").split(",")
ALLOWED_HOSTS = [] if not any(ALLOWED_HOSTS_PRE) else ALLOWED_HOSTS_PRE


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'login.apps.LoginConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'automactic.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'automactic.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / "static"

CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = (not DEBUG)
CSRF_COOKIE_SECURE = (not DEBUG)

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Logging

# Disable Django's logging setup
LOGGING_CONFIG = None


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)-15s | %(name)-26s | %(levelname)-8s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'standard_nodate': {
            'format': '%(asctime)-8s | %(process)-6s | %(name)-26s | %(levelname)-8s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'standard_nodate',
            'filename': 'logs/django.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
            'formatter': 'standard_nodate',
        }
    },
    'loggers': {
        'django.utils.autoreload': {
            'level': 'DEBUG',
            'handlers': ['null'],
            'propagate': False
        },
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
})

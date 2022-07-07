import os

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

SECRET_KEY = os.environ['AMAC_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

_hosts_with_spaces = os.environ.get('AMAC_ALLOWED_HOSTS', "").split(',')
ALLOWED_HOSTS = [] if not any(_hosts_with_spaces) else _hosts_with_spaces


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    'prod': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('AMAC_PG_DBNAME'),
        'USER': os.environ.get('AMAC_PG_USER'),
        'PASSWORD': os.environ.get('AMAC_PG_PASS'),
        'HOST': os.environ.get('AMAC_PG_HOST'),
        'PORT:': os.environ.get('AMAC_PG_PORT'),
    }
}
DATABASES['default'] = DATABASES['prod']

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-lk8%_7@n+%c=e$r0s$=t1exfj*sosqn$1mo*wd(7k9g_+3uxs0'
DEBUG = True
ALLOWED_HOSTS = ['*']

print('\033[91m' + 'USING BUILTIN SECRET KEY. DEBUG MODE ENABLED.' + '\033[0m')

DATABASES = {
    'dev': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
}
DATABASES['default'] = DATABASES['dev']

# For Django Debug Toolbar
INTERNAL_IPS = [
    "127.0.0.1",
]
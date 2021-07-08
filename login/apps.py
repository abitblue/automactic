import logging
import os

from django.apps import AppConfig

logger = logging.getLogger('Config')


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'

    def ready(self):
        logger.info('Starting automactic service')

        logger.debug('Creating superuser if it does not exist')
        try:
            from django.contrib.auth.models import User

            assert os.environ.get('AMAC_SUPERUSER_EMAIL') is not None, 'Undefined: AMAC_SUPERUSER_EMAIL'
            assert os.environ.get('AMAC_SUPERUSER_USERNAME') is not None, 'Undefined: AMAC_SUPERUSER_USERNAME'
            assert os.environ.get('AMAC_SUPERUSER_PASSWORD') is not None, 'Undefined: AMAC_SUPERUSER_PASSWORD'

            if not User.objects.filter(username__exact=os.environ['AMAC_SUPERUSER_USERNAME']).exists():
                User.objects.create_superuser(os.environ['AMAC_SUPERUSER_USERNAME'],
                                              os.environ['AMAC_SUPERUSER_EMAIL'],
                                              os.environ['AMAC_SUPERUSER_PASSWORD'])

        except Exception as err:
            logger.error(err)

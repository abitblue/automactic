import logging
import os


from django.apps import AppConfig
from django.db import connection


logger = logging.getLogger('Config')


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'

    def ready(self):
        logger.info('Starting automactic service')
        if all(x in connection.introspection.table_names() for x in ['login_usertype', 'login_user']):
            from .models import User
            logger.debug('Creating superuser if it does not exist')
            try:

                assert os.environ.get('AMAC_SUPERUSER_USERNAME') is not None, 'Undefined: AMAC_SUPERUSER_USERNAME'
                assert os.environ.get('AMAC_SUPERUSER_PASSWORD') is not None, 'Undefined: AMAC_SUPERUSER_PASSWORD'

                if not User.objects.filter(username__exact=os.environ['AMAC_SUPERUSER_USERNAME']).exists():
                    User.objects.create_superuser(os.environ['AMAC_SUPERUSER_USERNAME'],
                                                  os.environ['AMAC_SUPERUSER_PASSWORD'])

            except Exception as err:
                logger.error(err)

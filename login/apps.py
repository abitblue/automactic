import logging
import os

from django.apps import AppConfig
from django.db import connection
from interface.rotating_passwd import RotatingCode

logger = logging.getLogger('Config')


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'

    def ready(self):
        logger.info('Starting automactic service')
        if all(x in connection.introspection.table_names() for x in ['login_usertype', 'login_user']):
            from .models import User, UserType
            if not UserType.objects.filter(pk=1).exists():
                return

            logger.debug('Creating superuser and guest accounts if they don\'t exist')
            try:
                assert os.environ.get('AMAC_SUPERUSER_USERNAME') is not None, 'Undefined: AMAC_SUPERUSER_USERNAME'
                assert os.environ.get('AMAC_SUPERUSER_PASSWORD') is not None, 'Undefined: AMAC_SUPERUSER_PASSWORD'

                if not User.objects.filter(username__exact=os.environ['AMAC_SUPERUSER_USERNAME'].lower()).exists():
                    User.objects.create_superuser(os.environ['AMAC_SUPERUSER_USERNAME'],
                                                  os.environ['AMAC_SUPERUSER_PASSWORD'])

                if not User.objects.filter(username__exact='guest'):
                    guest = User.objects.create_user(username='guest', usertype=UserType.objects.get(name='Guest'),
                                                     password=str(RotatingCode.get()))
                    guest.bypass_rate_limit = True
                    guest.save()

            except Exception as err:
                logger.error(err)

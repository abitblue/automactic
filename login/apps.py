import logging
import os

from django.apps import AppConfig
from django.db import connection

from automactic import settings

logger = logging.getLogger('LoginConfig')


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'
    verbose_name = 'Authentication'

    def ready(self):

        if all(x in connection.introspection.table_names() for x in ['login_usertype', 'login_user']):
            from .models import User, UserType
            if not UserType.objects.filter(pk=1).exists():
                logger.warning('Missing default user types')
                return

            try:
                if 'AMAC_SUPERUSER_USERNAME' in os.environ \
                        and 'AMAC_SUPERUSER_PASSWORD' in os.environ \
                        and not User.objects.filter(username__exact=os.environ['AMAC_SUPERUSER_USERNAME'].lower()).exists():
                    User.objects.create_superuser(os.environ['AMAC_SUPERUSER_USERNAME'],
                                                  os.environ['AMAC_SUPERUSER_PASSWORD'])
                    logger.info('Created superuser account')

                if not User.objects.filter(username__exact='guest'):
                    guest = User.objects.create_user(username='guest', usertype=UserType.objects.get(name='Guest'),
                                                     password=settings.SECRET_KEY)
                    guest.bypass_rate_limit = True
                    guest.save()
                    logger.info('Created guest account')

            except Exception as err:
                logger.error(err)

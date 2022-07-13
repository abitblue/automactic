import logging
import os
import sys

from django.apps import AppConfig
from django.db import connection

logger = logging.getLogger('LoginConfig')


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'

    def ready(self):
        if not connection.introspection.table_names():
            logger.critical(f'Could not find any tables in the database. Did you migrate?')

        else:
            from .models import User
            if User.objects.count() == 0:

                assert os.environ['AMAC_ROOT_USER'], "Environment does not contain superuser username"
                assert os.environ['AMAC_ROOT_PASS'], "Environment does not contain superuser password"
                logger.info('No users yet. Creating superuser account.')
                root_username, root_password = os.environ['AMAC_ROOT_USER'], os.environ['AMAC_ROOT_PASS']
                User.objects.create_superuser(root_username, root_password)

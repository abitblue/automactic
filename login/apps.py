import logging
import os
import sys

from django.apps import AppConfig
from django.db import connection

logger = logging.getLogger('LoginConfig')


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'
    verbose_name = 'Authentication'

    def ready(self):
        if not connection.introspection.table_names():
            logger.critical(f'Could not find any tables in the database. Did you migrate?')

        else:
            from .models import User

            # No users exist yet, need to create superuser
            if User.objects.count() == 0:
                assert os.environ['AMAC_ROOT_USER'], "Environment does not contain superuser username"
                assert os.environ['AMAC_ROOT_PASS'], "Environment does not contain superuser password"

            root_user, root_pass = os.environ.get('AMAC_ROOT_USER', None), os.environ.get('AMAC_ROOT_PASS', None)
            if root_user and root_pass:
                logger.info('Ensuring superuser account exists')
                User.objects.try_create_superuser(root_user, root_pass)

            User.objects.try_create_superuser('deleted')

import logging
import os

from django.apps import AppConfig

logger = logging.getLogger('LoginConfig')


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'

    def ready(self):
        from .models import User

        if User.objects.count() == 0:
            assert os.environ['AMAC_ROOT_USERNAME'], "Environment does not contain superuser username"
            assert os.environ['AMAC_ROOT_PASSWORD'], "Environment does not contain superuser password"
            logger.info('No users yet. Creating superuser account.')
            root_username, root_password = os.environ['AMAC_ROOT_USERNAME'], os.environ['AMAC_ROOT_PASSWORD']
            User.objects.create_superuser(root_username, root_password)

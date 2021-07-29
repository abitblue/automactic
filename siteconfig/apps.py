from django.apps import AppConfig
from django.db import connection


class SiteConfigruationConfig(AppConfig):
    name = 'siteconfig'
    verbose_name = 'Logs and Configurations'

    def ready(self):
        if 'siteconfig_configuration' in connection.introspection.table_names():
            from .models import Configuration
            from .defaults import defaults

            Configuration.objects.bulk_create(defaults, ignore_conflicts=True)

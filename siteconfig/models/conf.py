import re

from django.core.exceptions import ValidationError
from django.db import models, connection

from siteconfig.defaults import defaults


class ConfigurationManager(models.Manager):
    def init_defaults(self):
        self.bulk_create([self.model(**default) for default in defaults], ignore_conflicts=True)

    def get_default(self, key):
        return self.model(**next(item for item in defaults if item['key'] == key))


class Configuration(models.Model):
    key = models.CharField(max_length=256, unique=True)
    value = models.TextField(blank=True, null=True)
    doc = models.TextField(blank=True, null=True)
    validator = models.TextField()

    objects = ConfigurationManager()

    class Meta:
        verbose_name = 'Site Config'
        verbose_name_plural = 'Site Config'

    def __str__(self):
        return self.key

    def clean_fields(self, exclude=None):
        super().clean_fields()
        if not re.match(self.validator, self.value):
            raise ValidationError("Value does not match regex validator")

    @classmethod
    def get(cls, key, cast=None, raw=False):
        obj = cls.objects.get_default(key)
        if 'siteconfig_configuration' in connection.introspection.table_names():
            obj = cls.objects.get(key=key)
        if raw:
            return obj.value
        if cast is not None:
            return [cast(item) for item in re.match(obj.validator, obj.value).groups()]
        return re.match(obj.validator, obj.value).groups()

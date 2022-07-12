from collections.abc import Callable
from datetime import datetime
from typing import Optional, Any

from django.db import models


class Datatype(models.IntegerChoices):
    BOOLEAN = 1
    INTEGER = 2
    STRING = 3
    # TODO: Timedelta
    # IPNetwork

    @staticmethod
    def conversion(item: int):
        _map = {
            1: bool,
            2: int,
            3: str
        }
        return _map[item]


class PermissionsManager(models.Manager):
    pass


class Permissions(models.Model):
    permission = models.CharField(max_length=160, unique=True)
    raw_value = models.TextField()
    type = models.IntegerField(choices=Datatype.choices)

    objects = PermissionsManager
    class Meta:
        verbose_name = 'Permissions and Settings'

    @property
    def value(self):
        return Datatype.conversion(self.type)(self._value)

    def get(self, permission_node: str, cast: Callable[[str], Any]):
        pass

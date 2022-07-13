from __future__ import annotations

import json
from django.db import models

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User


class Datatype(models.IntegerChoices):
    BOOLEAN = 1
    INTEGER = 2
    STRING = 3
    # TODO: Timedelta
    # IPNetwork

    @staticmethod
    def to_python(datatype: int):
        # From DB (str)
        _map = {
            1: lambda x: json.loads(x.lower()),
            2: lambda x: json.loads(x),
            3: lambda x: x
        }
        return _map[datatype]

    @staticmethod
    def to_db(datatype: int):
        # From Python (Any)
        _map = {
            1: lambda x: json.dumps(x),
            2: lambda x: json.dumps(x),
            3: lambda x: x
        }
        return _map[datatype]


class PermissionsManager(models.Manager):
    def get_raw_node(self, node_prefix: str):
        return self.filter(permission__istartswith=node_prefix)

    def get_user_node(self, user: User, node_suffix: str, *, default=None):
        if not node_suffix:
            raise NameError("Cannot query with an empty node")

        if filtered := self.get_raw_node(f'user/{user.username}/{node_suffix}'):
            return filtered.first().value

        group = user.type.name
        if filtered := self.get_raw_node(f'userType/{group}/{node_suffix}'):
            return filtered.first().value

        return default


class Permissions(models.Model):
    permission = models.CharField(max_length=160, unique=True)
    raw_value = models.CharField(max_length=160)
    type = models.IntegerField(choices=Datatype.choices)

    objects = PermissionsManager()

    class Meta:
        verbose_name = 'Permission'

    @property
    def value(self):
        return Datatype.to_python(self.type)(self.raw_value)

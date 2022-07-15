from __future__ import annotations

import json

from django.core.exceptions import ValidationError
from django.db import models

from typing import TYPE_CHECKING

from django.db.models import Q, Case, When, Count, QuerySet
from django.db.models.functions import Substr

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
            1: lambda x: bool(json.loads(x.lower())),
            2: lambda x: int(json.loads(x)),
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

    def get_raw_nodes(self, node_prefix: str):
        return self.filter(permission__istartswith=node_prefix)

    def get_user(self, user: User):
        # Substr is 1-indexed
        group_prefix = f'userType/{user.type}/'
        user_prefix = f'user/{user.username}/'

        # Grab all related permissions that start with `group_prefix` or `user_prefix`
        # Annotate them with the key suffix
        all_related_perms = (
            self.filter(Q(permission__startswith=group_prefix) | Q(permission__startswith=user_prefix))
                .annotate(suffix=Case(
                    When(permission__startswith=group_prefix, then=Substr('permission', len(group_prefix) + 1)),
                    When(permission__startswith=user_prefix, then=Substr('permission', len(user_prefix) + 1)),
                ))
        )

        # Of those related permissions, find duplicate suffixes
        unique_perm_nodes = (all_related_perms
                             .values('suffix')
                             .annotate(dcount=Count('suffix'))
                             .filter(dcount__gt=1)
                             .values_list('suffix', flat=True))

        # For each of the duplicates, prioritize the one that has the direct user, and exclude the ones for userType
        exclusion_list = [
            pk
            for node in unique_perm_nodes
            for pk in
            all_related_perms.filter(suffix=node, permission__startswith='userType').values_list('id', flat=True)
        ]
        return all_related_perms.exclude(id__in=exclusion_list)

    def get_user_node(self, user: User, node_suffix: str, *, default=None):
        if not node_suffix:
            raise NameError("Cannot query with an empty node")

        if filtered := self.get_raw_nodes(f'user/{user.username}/{node_suffix}'):
            return filtered.first().value

        group = user.type.name
        if filtered := self.get_raw_nodes(f'userType/{group}/{node_suffix}'):
            return filtered.first().value

        return default


class Permissions(models.Model):
    permission = models.CharField(max_length=160, unique=True)
    raw_value = models.CharField(max_length=160)
    type = models.IntegerField(choices=Datatype.choices)

    objects = PermissionsManager()

    class Meta:
        verbose_name = 'Permission'

    def __str__(self):
        return f'{self.permission} = {self.raw_value}'

    @property
    def value(self):
        return Datatype.to_python(self.type)(self.raw_value)

    def clean(self):
        super().clean()
        try:
            test_value = Datatype.to_python(self.type)(self.raw_value)
        except Exception as e:
            raise ValidationError(f'Could not interpret, "{self.raw_value}", as type, {Datatype(self.type).name}')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

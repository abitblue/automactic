from __future__ import annotations

import json
import re
import zoneinfo
from datetime import datetime, timezone

from django.core.exceptions import ValidationError
from django.db import models

from typing import TYPE_CHECKING, Optional
from netaddr import IPNetwork

from django.db.models import Q, Case, When, Count, Min
from django.db.models.functions import Substr

if TYPE_CHECKING:
    from .user import User
    from . import UserType


class WhenType:
    _validator = re.compile(r'^(0[1-9]|1[012]|[+-]\d+?)/(0[1-9]|[12][0-9]|3[01]|[+-]\d+?)/(\d{4}|[+-]\d+?)$')

    def __init__(self, offset_str: str):
        self._offset_str = offset_str
        self._matched = self._validator.match(offset_str)
        if not self._matched:
            raise ValidationError(f"Invalid schema: {offset_str}")

    def as_datetime(self, reftime: datetime = None) -> datetime:
        if reftime is None:
            reftime = datetime.today()

        # Evaluate each group to form the date
        m, d, y = tuple(map(lambda ofst, ref: ref + eval(ofst) if ofst[0] in '+-' else int(ofst),
                            self._matched.groups(),
                            (reftime.month, reftime.day, reftime.year)
                            ))

        return datetime(y, m, d, tzinfo=zoneinfo.ZoneInfo("America/New_York"))

    def __str__(self):
        return self._offset_str

    def __eq__(self, other: WhenType):
        return self._offset_str == other._offset_str


class Datatype(models.IntegerChoices):
    NULL = 0
    BOOLEAN = 1
    INTEGER = 2
    STRING = 3
    FLOAT = 4
    TIMEDELTA = 5
    IPNetwork = 6

    @staticmethod
    def to_python(datatype: int):
        # From DB (str) -> Python (Any)
        _map = {
            0: lambda x: None,
            1: lambda x: bool(json.loads(x.lower())),
            2: lambda x: int(json.loads(x)),
            3: lambda x: x,
            4: lambda x: float(json.loads(x)),
            5: lambda x: WhenType(x),
            6: lambda x: IPNetwork(x)
        }
        return _map[datatype]

    @staticmethod
    def to_db(datatype: int):
        # From Python (Any) -> DB (str)
        _map = {
            0: lambda x: json.dumps(x),
            1: lambda x: json.dumps(x),
            2: lambda x: json.dumps(x),
            3: lambda x: x,
            4: lambda x: json.dumps(x),
            5: lambda x: str(x),
            6: lambda x: str(x)
        }
        return _map[datatype]


class PermissionsManager(models.Manager):

    def get_raw_nodes(self, node_prefix: str):
        return self.filter(permission__istartswith=node_prefix)

    def get_bulk(self, user: Optional[User] = None, usertype: Optional[UserType] = None,
                 *, query_user=True, query_group=True, query_global=True):

        if user is None:
            query_user = False
        else:
            usertype = user.type

        if usertype is None:
            query_group = False

        # Substr is 1-indexed
        user_prefix = f'user/{user.username}/' if query_user else 'NULL'
        group_prefix = f'userType/{usertype}/' if query_group else 'NULL'
        global_prefix = 'global/' if query_global else 'NULL'

        # Grab all related permissions that start with `group_prefix` or `user_prefix`
        # Annotate them with the key suffix
        all_related_perms = (
            self.filter(
                Q(permission__startswith=group_prefix)
                | Q(permission__startswith=user_prefix)
                | Q(permission__startswith=global_prefix))
            .annotate(suffix=Case(
                When(permission__startswith=user_prefix, then=Substr('permission', len(user_prefix) + 1)),
                When(permission__startswith=group_prefix, then=Substr('permission', len(group_prefix) + 1)),
                When(permission__startswith=global_prefix, then=Substr('permission', len(global_prefix) + 1)),
            ), priority=Case(
                When(permission__startswith=user_prefix, then=1),
                When(permission__startswith=group_prefix, then=2),
                When(permission__startswith=global_prefix, then=3),
            ))
        )

        # Of those related permissions, find duplicate suffixes, and lowest available priority
        unique_perm_nodes = (all_related_perms
                             .values('suffix')
                             .annotate(dcount=Count('suffix'))
                             .filter(dcount__gt=1)
                             .values_list('suffix', flat=True))

        # For each of the duplicates, perform priority: user -> userType -> Global
        lowest_priority = lambda s: all_related_perms.filter(suffix=s).aggregate(Min('priority'))['priority__min']
        exclusion_list = [
            pk
            for node in unique_perm_nodes
            for pk in
            all_related_perms.filter(
                Q(suffix=node) & ~Q(priority=lowest_priority(node))
            ).values_list('id', flat=True)
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

        if filtered := self.get_raw_nodes(f'global/{node_suffix}'):
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
        value = self.value
        if str(value) != self.raw_value:
            return f'{self.permission} = {self.value} ({self.raw_value})'
        return f'{self.permission} = {self.value}'

    @property
    def value(self):
        return Datatype.to_python(self.type)(self.raw_value)

    def clean(self):
        super().clean()
        try:
            decoded1 = Datatype.to_python(self.type)(self.raw_value)
            encoded = Datatype.to_db(self.type)(decoded1)
            decoded2 = Datatype.to_python(self.type)(encoded)

            assert decoded1 == decoded2

        except Exception as e:
            raise ValidationError(f'Could not interpret, "{self.raw_value}", as type, {Datatype(self.type).name}')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

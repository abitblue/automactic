from collections.abc import Callable
from datetime import datetime
from typing import Optional, Any

from django.db import models


class Permissions(models.Model):
    permission = models.CharField(max_length=160, unique=True)
    value = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Permissions and Settings'

    def get(self, permission_node: str, cast: Callable[[str], Any]):
        pass

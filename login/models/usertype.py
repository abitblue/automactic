from collections.abc import Callable
from datetime import datetime
from typing import Optional, Any

from django.db import models


class UserType(models.Model):
    name = models.CharField(max_length=50)

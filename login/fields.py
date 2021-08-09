import re

from django.core.validators import RegexValidator
from django.db import models


class WhenField(models.CharField):
    when_validate = re.compile(r'^(0[1-9]|1[012]|[+-]\d+?)/(0[1-9]|[12][0-9]|3[01]|[+-]\d+?)/(\d{4}|[+-]\d+?)$')

    default_validators = [RegexValidator(regex=when_validate)]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 16
        super().__init__(*args, **kwargs)


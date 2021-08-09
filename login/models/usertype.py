from datetime import datetime
from typing import Optional

from django.db import models

from login.fields import WhenField


class UserType(models.Model):
    name = models.CharField(max_length=160)
    clearpass_device_expire = WhenField(blank=True, null=True)
    device_modified_warning_count = models.PositiveIntegerField(blank=True, null=True,
                                                                help_text="Blank values mean never warn")

    class Meta:
        verbose_name = 'User Type'

    def __str__(self):
        return self.name

    def get_clearpass_device_expire_time(self) -> Optional[datetime]:
        if self.clearpass_device_expire is None:
            return None

        def _update_val(val, reftime):
            return reftime + eval(val) if val[0] in ('+', '-') else int(val)

        val_groups = WhenField.when_validate.match(self.clearpass_device_expire).groups()
        m, d, y = tuple(map(_update_val,
                            val_groups,
                            (datetime.today().month, datetime.today().day, datetime.today().year)
                            ))
        return datetime(y, m, d).astimezone()

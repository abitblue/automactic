from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserType(models.Model):
    name = models.CharField(max_length=160)
    disable_in = models.DurationField(null=True,
                                      help_text="When to disable the user account. Blank values mean never disable")
    device_limit = models.PositiveIntegerField(blank=True, null=True,
                                               help_text="Blank values mean no limit")
    device_validity_period = models.DurationField(null=True,
                                                  help_text="Clearpass device expiry. Blank values mean never expire")
    modified_warning_threshold = models.PositiveIntegerField(blank=True, null=True,
                                                             help_text="Blank values mean never warn")

    class Meta:
        verbose_name = 'User Type'

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.ForeignKey(UserType, on_delete=models.PROTECT)
    modified_count = models.PositiveIntegerField(default=0)
    disable_on = models.DateField(blank=True, null=True, help_text="Implicitly defined by profile type")

    # Values implicitly inherited from user_type
    device_limit = models.PositiveIntegerField(blank=True, null=True, help_text="Implicitly defined by profile type")
    device_validity_period = models.DurationField(blank=True, null=True, help_text="Implicitly defined by profile type")
    modified_warning_threshold = models.PositiveIntegerField(blank=True, null=True, help_text="Implicitly defined by profile type")

    @property
    def _device_limit(self):
        return self.type.device_limit if self.device_limit is None else self.device_limit

    @property
    def _modified_warning_threshold(self):
        return self.type.modified_warning_threshold if self.modified_warning_threshold is None else self.modified_warning_threshold

    @property
    def _device_validity_period(self):
        return self.type.device_validity_period if self.device_validity_period is None else self.device_validity_period

    def save(self, *args, **kwargs):
        if self._state.adding and self.disable_on is None:
            self.disable_on = timezone.now() + self.type.disable_in
        super().save(*args, **kwargs)

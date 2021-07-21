from django.contrib import admin
from django.db import models


class UserType(models.Model):
    name = models.CharField(max_length=160)
    disable_in = models.DurationField(null=True,
                                      help_text="When to disable the user account. Blank values mean never disable")
    device_validity_period = models.DurationField(null=True,
                                                  help_text="Clearpass device expiry. Blank values mean never expire")
    device_modified_warning_count = models.PositiveIntegerField(blank=True, null=True,
                                                                help_text="Blank values mean never warn")

    class Meta:
        verbose_name = 'User Type'

    def __str__(self):
        return self.name

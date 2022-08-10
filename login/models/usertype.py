from django.db import models

from .permissions import Permissions


class UserType(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'User Type'

    def __str__(self):
        return f'{self.name}'

    def get_permissions(self):
        return Permissions.objects.get_bulk(usertype=self, query_global=False)

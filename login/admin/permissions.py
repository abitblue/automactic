from django.contrib import admin

from login.models import Permissions


@admin.register(Permissions)
class PermissionsAdmin(admin.ModelAdmin):
    # TODO: Add display for permissions
    list_display = ('permission', 'value', 'type')
    search_fields = ('permission', )
    ordering = ('permission',)

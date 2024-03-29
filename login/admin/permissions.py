from django.contrib import admin
from django.http import HttpRequest

from login.models import Permissions


@admin.register(Permissions)
class PermissionsAdmin(admin.ModelAdmin):
    list_display = ('permission', 'raw_value', 'value', 'type')
    search_fields = ('permission', )
    search_help_text = "Searches filter by permission node"
    ordering = ('id', 'permission',)
    list_filter = ('type',)

    def has_change_permission(self, request: HttpRequest, obj: Permissions = None):
        # In general, people with access to the admin site have access
        if obj is None:
            return True

        if obj.permission.startswith('userType/Superuser'):
            return False
        return True

    def has_delete_permission(self, request: HttpRequest, obj: Permissions = None):
        # If you can change, you can delete
        return self.has_change_permission(request, obj)

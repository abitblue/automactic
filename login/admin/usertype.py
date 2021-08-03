from django.contrib import admin

from login.models import UserType


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_validity_period', 'device_modified_warning_count',)
    search_fields = ('name',)
    ordering = ('id',)

    # Cannot delete user types. Prevents user error
    def has_delete_permission(self, request, obj=None):
        return False

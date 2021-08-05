from django.contrib import admin

from login.models import UserType


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_validity_period', 'device_modified_warning_count',)
    search_fields = ('name',)
    ordering = ('id',)

    # Cannot delete default user types. Manually created ones are still deletable.
    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return False

        if obj.name in ['Staff', 'Sentinel', 'Guest', 'Student']:
            return False
        return True

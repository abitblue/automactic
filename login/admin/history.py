from django.contrib import admin

from login.models import LoginHistory


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('time', 'user', 'mac_address', 'host', 'logged_in', 'mac_updated')
    search_fields = ('user__username', 'mac_address', 'host')
    list_filter = ('time', 'logged_in', 'mac_updated', 'user__type')
    ordering = ('time', )

    # Cannot modify table from admin site
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from login.models import LoginHistory


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'get_user', 'mac_address', 'host', 'logged_in', 'mac_updated')
    search_fields = ('id', 'user__username', 'mac_address', 'host')
    search_help_text = "Searches filter by id, username, mac adddress, and host"
    list_filter = ('time', 'logged_in', 'mac_updated', 'user__type')
    ordering = ('time', )

    @admin.display(description='User')
    def get_user(self, obj: LoginHistory):
        return mark_safe('<a href={}>{}</a>'.format(
            reverse('admin:login_user_change', args=(obj.user.pk,)),
            obj.user
        ))

    # Cannot modify table from admin site
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

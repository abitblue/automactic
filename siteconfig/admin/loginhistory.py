from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.utils.safestring import mark_safe

from siteconfig.models import LoginHistory, LastLoginAttempt


class MacIsNoneFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'MAC Address is null'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'is_macnull'

    def lookups(self, request, model_admin):
        return (
            (1, 'Null'),
            (0, 'Non-Null')
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(Q(mac_address__isnull=True))
        elif self.value() == '0':
            return queryset.filter(Q(mac_address__isnull=False))


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('time', 'user', 'logged_in', 'mac_address')
    search_fields = ('user__username', 'mac_address')
    list_filter = ('time', 'logged_in', 'user__type', MacIsNoneFilter)
    ordering = ('time',)
    readonly_fields = ('time', 'user', 'logged_in', 'mac_address')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LastLoginAttempt)
class LastLoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('ip', 'time')
    search_fields = ('ip',)
    ordering = ('time',)
    readonly_fields = ('ip', 'time')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


from django.contrib.sessions.models import Session
from pprint import pformat
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'get_session_data', 'expire_date']
    search_fields = ('session_key',)
    ordering = ('expire_date',)

    def get_session_data(self, obj: Session):
        return mark_safe(f'<pre style="margin: 0em 0em;">{pformat(obj.get_decoded())}</pre>')


    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


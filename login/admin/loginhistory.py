from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from login.models import LoginHistory


class MacIsNoneFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'MAC Address is null'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'is_macnuull'

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
    search_fields = ('user', 'mac_address')
    list_filter = ('time', 'logged_in', MacIsNoneFilter)
    ordering = ('time',)
    readonly_fields = ('time', 'user', 'logged_in', 'mac_address')

    def has_add_persmission(self, request, obj=None):
        return False
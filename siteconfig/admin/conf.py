from django.contrib import admin

from siteconfig.models import Configuration


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ('key',)
    ordering = ('key',)
    readonly_fields = ('key', 'validator', 'doc')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

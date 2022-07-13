from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# from login.forms import UserChangeForm, UserCreationForm
from login.models import User
from django.db.models import QuerySet
from django.http import HttpRequest


@admin.action(description='Reset MAC modifications')
def reset_modified(self: User, request: HttpRequest, queryset: QuerySet):
    queryset.update(mac_modifications=0)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('is_active', 'username', 'get_type', 'get_modifications', 'last_login')
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('type__name', 'is_active')
    ordering = ('username',)
    actions = [reset_modified]

    @admin.display(description='Type')
    def get_type(self, obj: User):
        if obj.is_staff:
            return f'{obj.type!s} (Site Admin)'
        return f'{obj.type!s}'

    @admin.display(description='Modifications')
    def get_modifications(self, obj: User):
        limit = obj.get_permission("warningThreshold", default=None)
        return f'{obj.mac_modifications} / {limit if limit else "-"}'

    # Django Default Admin Site Compatibility:
    filter_horizontal = ()
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'type'),
        }),
    )

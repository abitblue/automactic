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
    list_display = ('is_active', 'username', 'type', 'mac_modifications', 'last_login')
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('type__name', 'is_active')
    ordering = ('username',)
    actions = [reset_modified]

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

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from login.forms import UserChangeForm, UserCreationForm
from login.models import User


@admin.action(description='Reset modified count')
def reset_modified(modeladmin, request, queryset):
    queryset.update(device_modified_count=0)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        'username', 'get_type', 'get_modified_warning_threshold')
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('is_staff', 'type__name')
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'is_staff', 'bypass_rate_limit')
        }),
        ('Profile', {
            'fields': ('type', '_device_modified_warning_count', 'device_modified_count')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_staff', 'bypass_rate_limit'),
        }),
        ('Profile',
         {'fields': ('type', '_device_modified_warning_count', 'device_modified_count')}),
    )
    ordering = ('username',)
    filter_horizontal = ()
    readonly_fields = ('device_modified_count',)
    actions = [reset_modified]

    @admin.display(description='Type')
    def get_type(self, obj: User):
        if obj.is_staff:
            return f'{obj.type} (Site Admin)'
        return str(obj.type)

    @admin.display(description='Modified Warning Threshold')
    def get_modified_warning_threshold(self, obj: User):
        return f'{obj.device_modified_count} / {(lambda x: "-" if x is None else x)(obj.device_modified_warning_count)}'

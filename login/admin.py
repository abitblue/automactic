from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

from .models import UserType, Profile

admin.site.site_header = 'automactic'
admin.site.index_title = 'Administrative Portal'


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'disable_in', 'device_limit', 'device_validity_period', 'modified_warning_threshold',)
    search_fields = ('name',)


@admin.action(description='Reset modified count')
def reset_modified(modeladmin, request, queryset):
    queryset.update(modified_count=0)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
    'get_user', 'type', 'disable_on', '_device_limit', '_device_validity_period', 'get_modified_warning_threshold',)
    search_fields = ('user__username',)
    list_filter = ('type', 'user__is_active')
    readonly_fields = ('modified_count',)
    actions = [reset_modified]

    @admin.display(description='User')
    def get_user(self, obj: Profile):
        return format_html(f'<a href={reverse("admin:auth_user_change", args=(obj.user.id,))}>{obj.user.username}</a>')

    @admin.display(description='Modified Warning Threshold')
    def get_modified_warning_threshold(self, obj: Profile):
        return f'{obj.modified_count} / {(lambda x: "-" if x is None else x)(obj._modified_warning_threshold)}'


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profiles'
    readonly_fields = ('modified_count',)


# Re-register user admin page
admin.site.unregister(User)
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

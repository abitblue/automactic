from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils import timezone

from .forms import UserChangeForm, UserCreationForm
from .models import UserType, User

admin.site.site_header = 'automactic'
admin.site.index_title = 'Administrative Portal'


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'disable_in', 'device_validity_period', 'device_modified_warning_count',)
    search_fields = ('name',)
    ordering = ('id',)

    # Cannot delete user types. Prevents user error
    def has_delete_permission(self, request, obj=None):
        return False


@admin.action(description='Reset modified count')
def reset_modified(modeladmin, request, queryset):
    queryset.update(device_modified_count=0)


class IsActiveFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'is active'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            (1, 'Yes'),
            (0, 'No')
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(Q(disable_on__gt=timezone.now()) | Q(disable_on__isnull=True))
        elif self.value() == '0':
            return queryset.filter(disable_on__lte=timezone.now())


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        'username', 'get_type', 'disable_on', 'get_device_validity_period',
        'get_modified_warning_threshold')
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('is_staff', IsActiveFilter)
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'is_staff', 'bypass_rate_limit')
        }),
        ('Profile', {
            'fields': ('type', 'disable_on', '_device_validity_period', '_device_modified_warning_count',
                       'device_modified_count')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_staff', 'bypass_rate_limit'),
        }),
        ('Profile',
         {'fields': ('type', 'disable_on', '_device_validity_period', '_device_modified_warning_count',
                     'device_modified_count')}),
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

    @admin.display(description='Device Validity Period')
    def get_device_validity_period(self, obj: User):
        return obj.device_validity_period

    @admin.display(description='Modified Warning Threshold')
    def get_modified_warning_threshold(self, obj: User):
        return f'{obj.device_modified_count} / {(lambda x: "-" if x is None else x)(obj.device_modified_warning_count)}'


# Remove Groups from admin page
admin.site.unregister(Group)

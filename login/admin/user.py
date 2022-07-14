from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# from login.forms import UserChangeForm, UserCreationForm
from login.models import User, UserSession
from django.db.models import QuerySet
from django.http import HttpRequest


@admin.action(description='Reset MAC modifications')
def reset_modified(model_admin, request: HttpRequest, queryset: QuerySet):
    queryset.update(mac_modifications=0)


@admin.action(description='Remove sessions')
def remove_sessions(model_admin, request: HttpRequest, queryset: QuerySet):
    for user in queryset:
        user_sessions = UserSession.objects.filter(user=user)

        # Remove the actual sessions
        for session_obj in user_sessions:
            session_obj.session.delete()

        # Remove the sessions from the linked DB
        user_sessions.delete()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('is_active', 'username', 'get_type', 'get_modifications', 'last_login')
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('type__name', 'is_active')
    ordering = ('username',)
    actions = [reset_modified, remove_sessions]

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
            'fields': ('username', 'password', 'type', 'get_permissions')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'type'),
        }),
    )
    readonly_fields = ('get_permissions',)

    @admin.display(description='Permissions')
    def get_permissions(self, obj: User):
        return 'Test!'

    # Cannot change superusers from admin site unless also a superuser
    def has_change_permission(self, request: HttpRequest, obj: User = None):
        # In general, people with access to the admin site have access
        if obj is None:
            return True

        # Superusers always have access
        if request.user.type.name == 'Superuser':
            return True
        elif obj.type.name == 'Superuser':
            return False

        return True

    def has_delete_permission(self, request: HttpRequest, obj: User = None):
        # If you can change, you can delete
        return self.has_change_permission(request, obj)

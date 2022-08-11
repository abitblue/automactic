from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# from login.forms import UserChangeForm, UserCreationForm
from django.urls import reverse
from django.utils import timezone
from django.utils.html import linebreaks
from django.utils.safestring import mark_safe

from login.models import User, UserSession, LoginHistory
from django.db.models import QuerySet
from django.http import HttpRequest


@admin.action(description='Reset MAC modifications')
def reset_modified(model_admin, request: HttpRequest, queryset: QuerySet):
    queryset.update(mac_modifications=0)


@admin.action(description='Set inactive')
def set_inactive(model_admin, request: HttpRequest, queryset: QuerySet):
    queryset.update(is_active=False)


@admin.action(description='Set active')
def set_active(model_admin, request: HttpRequest, queryset: QuerySet):
    queryset.update(is_active=True, start_time=timezone.now())


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
    list_display = ('is_active', 'username', 'get_type', 'get_modifications', 'last_login', 'start_time')
    list_display_links = ('username',)
    search_fields = ('username',)
    search_help_text = "Searches filter by username"
    list_filter = ('type__name', 'is_active')
    ordering = ('username',)
    actions = [reset_modified, set_inactive, set_active, remove_sessions]

    @admin.display(description='Type')
    def get_type(self, obj: User):
        if obj.is_staff:
            return f'{obj.type!s} (Site Admin)'
        return f'{obj.type!s}'

    @admin.display(description='Modifications')
    def get_modifications(self, obj: User):
        limit = obj.get_permission("warningThreshold", default=None)
        return f'{obj.mac_modifications} / {limit if limit else "-"}'

    @admin.display(description='Permissions')
    def get_permissions(self, obj: User):
        return mark_safe(linebreaks(
            '\n'.join(
                '<a href="{}">{}</a>'.format(
                    reverse("admin:login_permissions_change", args=(item.pk,)),
                    str(item)
                ) if str(item).startswith('user/') else str(item)
                for item in obj.permissions().iterator()
            ) + f'\n\n<a href={reverse("admin:login_permissions_add")}?permission=user/{obj.username}/>'
                f'(+ Add a new permission for this user)</a>'
        ))

    @admin.display(description='Login History')
    def get_login_history(self, obj: User):
        history = LoginHistory.objects.filter(user=obj)
        return mark_safe('\n'.join(
            '<pre style="margin: 0em 0em;"><a href="{}">{}</a></pre>'.format(
                reverse("admin:login_loginhistory_change", args=(history_obj.pk,)),
                history_obj.concise_str
            )
            for history_obj in history.iterator()
        ))

    @admin.display(description='Sessions')
    def get_sessions(self, obj: User):
        session_keys = UserSession.objects.filter(user=obj).values_list('session_key', flat=True)
        return mark_safe(linebreaks('\n'.join(
            '<a href="{}">{}</a>'.format(
                reverse("admin:sessions_session_change", args=(key,)),
                key
            )
            for key in session_keys.iterator()
        )))

    # Django Default Admin Site Compatibility:
    filter_horizontal = ()
    fieldsets = (
        (None, {
            'classes': ('',),
            'fields': ('username', 'password', 'type')
        }),
        ('Permissions', {
            'classes': ('',),
            'fields': ('get_permissions',),
        }),
        ('Account History', {
            'classes': ('',),
            'fields': ('get_login_history', 'get_sessions'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'type'),
        }),
    )
    readonly_fields = ('get_permissions', 'get_login_history', 'get_sessions')

    # Cannot change superusers from admin site unless also a superuser
    def has_change_permission(self, request: HttpRequest, obj: User = None):
        # In general, people with access to the admin site have access
        if obj is None:
            return True

        # Superusers always have access
        if request.user.type.name.lower() == 'superuser':
            return True
        elif obj.type.name.lower() == 'superuser':
            return False

        return True

    def has_delete_permission(self, request: HttpRequest, obj: User = None):
        # If you can change, you can delete
        return self.has_change_permission(request, obj)

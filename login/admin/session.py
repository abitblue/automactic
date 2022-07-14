from pprint import pformat

from django.contrib import admin
from django.contrib.sessions.models import Session
from django.utils.safestring import mark_safe

from login.models import UserSession


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'get_session_data', 'expire_date']
    search_fields = ('session_key',)
    ordering = ('expire_date',)

    @admin.display(description='Session Data')
    def get_session_data(self, obj: Session):
        return mark_safe(f'<pre style="margin: 0em 0em;">{pformat(obj.get_decoded())}</pre>')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

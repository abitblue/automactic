from django.contrib import admin
from django.utils.html import linebreaks
from django.utils.safestring import mark_safe

from login.models import UserType


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'permissions')
    search_fields = ('name',)
    search_help_text = "Searches filter by name"
    ordering = ('id',)

    @admin.display(description='Permissions')
    def permissions(self, obj: UserType):
        return mark_safe(linebreaks(
            '\n'.join(f'{item!s}' for item in obj.get_permissions().iterator())
        ))

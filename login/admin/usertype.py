from django.contrib import admin

from login.models import UserType


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    # TODO: Add display for permissions
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('id',)

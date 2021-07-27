from django.contrib import admin as admin
from django.contrib.auth.models import Group

from .loginhistory import LoginHistoryAdmin
from .user import UserAdmin
from .usertype import UserTypeAdmin

# Remove Groups from admin page
admin.site.unregister(Group)

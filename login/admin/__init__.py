from django.contrib import admin as admin
from django.contrib.auth.models import Group

from .user import UserAdmin
from .usertype import UserTypeAdmin
from .permissions import PermissionsAdmin
from .history import LoginHistoryAdmin
from .session import SessionAdmin

# Remove Groups from admin page
admin.site.unregister(Group)

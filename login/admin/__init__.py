from django.contrib import admin as dadmin
from django.contrib.auth.models import Group

from .loginhistory import LoginHistoryAdmin
from .user import UserAdmin
from .usertype import UserTypeAdmin


dadmin.site.site_header = 'automactic'
dadmin.site.index_title = 'Administrative Portal'

# Remove Groups from admin page
dadmin.site.unregister(Group)

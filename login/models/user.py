from functools import cached_property

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .usertype import UserType
from .permissions import Permissions


def get_sentinel_user():
    return get_user_model().objects.get(username='deleted')


class UserManager(BaseUserManager):
    def create_user(self, username: str, usertype: UserType, password=None):
        if not username:
            raise ValueError('Users must have a username')

        user: User = self.model(username=username, type=usertype)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username: str, password=None):
        # Create 'Admin' group if not already made. Then, create the user like normal.
        admin_type, created = UserType.objects.get_or_create(name='Superuser')
        return self.create_user(username, admin_type, password)

    def try_create_superuser(self, username: str, password=None):
        if user := self.filter(username=username):
            return user.first(), False
        return self.create_superuser(username, password), True


class User(AbstractBaseUser):
    """
    The custom user model for the site.
    Usernames are always stored and accessed as lower-case values.
    Username, password, and usertype are required.
    """
    # TODO: Refer to scratch.txt. Still missing fields.
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=50,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists",
        })

    # Prevent accidental deletions of UserTypes. All Users of that usertype must be deleted first.
    type = models.ForeignKey('UserType', on_delete=models.PROTECT)

    # Accounts shouldn't get deleted by default, to keep user history available.
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether user should be treated as active. Unselect this instead of deleting accounts."
    )

    # The number of times the MAC address has been modified
    mac_modifications = models.PositiveIntegerField(default=0)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['type']

    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    def permissions(self):
        return Permissions.objects.get_user(self)

    def get_permission(self, node: str, *, default=None):
        return Permissions.objects.get_user_node(self, node, default=default)

    # Django Default Admin Site Compatibility:
    class Meta:
        verbose_name = 'User'

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    @cached_property
    def is_staff(self):
        """Returns true if the user is allowed to access the admin portal"""
        return Permissions.objects.get_user_node(self, 'adminSiteAccess', default=False)

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

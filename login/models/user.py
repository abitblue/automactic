from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .usertype import UserType


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
        if user := self.filter(username=username).first():
            return user, False
        return self.create_superuser(username, password)


class User(AbstractBaseUser):
    """
    The custom user model for the site.
    Usernames are always stored and accessed as lower-case values.
    Username, password, and usertype are required.
    """
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

    # Django Default Admin Site Compatibility:
    class Meta:
        verbose_name = 'User'

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    @property
    def is_staff(self):
        """Returns true if the user is allowed to access the admin portal"""
        # TODO: Read permission DB
        return True

    def has_perm(self, perm, obj=None):
        if self.is_staff:
            return True
        return False

    def has_module_perms(self, app_label):
        if self.is_staff:
            return True
        return False

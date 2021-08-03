from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone

from .usertype import UserType


class UserManager(BaseUserManager):
    def create_user(self, username: str, usertype: UserType, password=None):
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(username=username, type=usertype)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username,
                                UserType.objects.get(name='Sentinel'),
                                password=password)
        user.is_staff = True
        user.bypass_rate_limit = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class User(AbstractBaseUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        })

    is_staff = models.BooleanField(
        'admin',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )

    type = models.ForeignKey(UserType, on_delete=models.PROTECT, related_name='users')
    device_modified_count = models.PositiveIntegerField(default=0)
    bypass_rate_limit = models.BooleanField(default=False,
                                            help_text='Rate limits help against brute force attacks, but cause issues '
                                                      'when troubleshooting. Use with caution.')

    # Values implicitly inherited from user type
    _device_validity_period = models.DurationField(blank=True, null=True,
                                                   help_text="Implicitly defined by profile type. Write to override.")
    _device_modified_warning_count = models.PositiveIntegerField(blank=True, null=True,
                                                                 help_text="Implicitly defined by profile type. Write to override.")

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['type']

    @property
    def is_active(self):
        return True

    @property
    def device_modified_warning_count(self):
        return self.type.device_modified_warning_count if self._device_modified_warning_count is None else self._device_modified_warning_count

    @property
    def device_validity_period(self):
        return self.type.device_validity_period if self._device_validity_period is None else self._device_validity_period

    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        if self.is_staff:
            return True
        return False

    def has_module_perms(self, app_label):
        if self.is_staff:
            return True
        return False

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

import logging
from typing import Union, Optional

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from macaddress.fields import MACAddressField


class UserType(models.Model):
    name = models.CharField(max_length=160)
    disable_in = models.DurationField(null=True,
                                      help_text="When to disable the user account. Blank values mean never disable")
    device_limit = models.PositiveIntegerField(blank=True, null=True,
                                               help_text="Blank values mean no limit")
    device_validity_period = models.DurationField(null=True,
                                                  help_text="Clearpass device expiry. Blank values mean never expire")
    modified_warning_threshold = models.PositiveIntegerField(blank=True, null=True,
                                                             help_text="Blank values mean never warn")

    class Meta:
        verbose_name = 'User Type'

    def __str__(self):
        return self.name


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
        user.save(using=self._db)
        return user


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
    disable_on = models.DateTimeField(blank=True, null=True,
                                      help_text='When to disable user account. Implicitly defined by user type.')
    device_limit = models.PositiveIntegerField(blank=True, null=True,
                                               help_text="Implicitly defined by profile type. Write to override.")
    device_validity_period = models.DurationField(blank=True, null=True,
                                                  help_text="Implicitly defined by profile type. Write to override.")
    device_modified_warning_count = models.PositiveIntegerField(blank=True, null=True,
                                                                help_text="Implicitly defined by profile type. Write to override.")
    modified_warning_threshold = models.PositiveIntegerField(blank=True, null=True,
                                                             help_text="Implicitly defined by profile type Write to override.")

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['type']

    @property
    def is_active(self):
        if self.disable_on is None:
            return True
        return timezone.now() <= self.disable_on

    @property
    def _device_limit(self):
        return self.type.device_limit if self.device_limit is None else self.device_limit

    @property
    def _modified_warning_threshold(self):
        return self.type.modified_warning_threshold if self.modified_warning_threshold is None else self.modified_warning_threshold

    @property
    def _device_validity_period(self):
        return self.type.device_validity_period if self.device_validity_period is None else self.device_validity_period

    def save(self, *args, **kwargs):
        if self._state.adding and self.disable_on is None and self.type.disable_in is not None:
            self.disable_on = timezone.now() + self.type.disable_in
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


class LoginHistory(models.Model):
    _logger = logging.getLogger('LoginLog')

    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loginlog')
    logged_in = models.BooleanField(help_text='Did the user enter the correct password?')
    mac_address = MACAddressField(null=True, help_text='MAC Addr of new device. Null means did not register,')

    @classmethod
    def log(cls, user: Union[User, str], logged_in: bool, mac_address: Optional[str] = None):
        userobj = user
        if isinstance(user, str):
            userqs = User.objects.filter(username__exact=user)
            if not userqs.exists():
                return False
            userobj = userqs.first()
        try:
            cls.objects.create(user=userobj, logged_in=logged_in, mac_address=mac_address)
            return True
        except Exception as err:
            cls._logger.error(err)
            return False

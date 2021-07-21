import logging
from typing import Union, Optional

from django.db import models
from macaddress.fields import MACAddressField

from . import User


class LoginHistory(models.Model):
    _logger = logging.getLogger('LoginLog')

    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loginlog')
    logged_in = models.BooleanField(help_text='Did the user enter the correct password?')
    mac_address = MACAddressField(null=True, help_text='MAC Addr of new device. Null means did not register,')

    class Meta:
        verbose_name = "Login History"
        verbose_name_plural = "Login History"

    def __str__(self):
        return f'Login by {self.user} on {self.time.strftime("%b %d, %Y")} at {self.time.strftime("%I:%M:%S %p")}'

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

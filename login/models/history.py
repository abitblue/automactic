from django.db import models
from macaddress.fields import MACAddressField

from .user import User, get_sentinel_user


class LoginHistory(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), related_name='logins')
    mac_address = MACAddressField(null=True, integer=False)
    host = models.TextField()
    logged_in = models.BooleanField(default=False)
    mac_updated = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Login History'
        verbose_name_plural = 'Login History'

    @property
    def concise_str(self):
        success = 'T' if self.logged_in else 'F'
        updated = f'T: {self.mac_address}' if self.mac_updated else 'F'
        return f'{self.time.isoformat(sep=" ", timespec="seconds")} : {success} {updated}'

    def __str__(self):
        return f'Login by {self.user} on {self.time.strftime("%b %d, %Y")} at {self.time.strftime("%I:%M:%S %p")}'




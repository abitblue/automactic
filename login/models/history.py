import logging
from typing import Optional, Union

from django.db import models
from django.http import HttpRequest
from django.utils import timezone
from ipware import get_client_ip
from macaddress.fields import MACAddressField

from .user import User, get_sentinel_user
from ..utils import MACAddress


class LoginHistory(models.Model):
    _logger = logging.getLogger('LoginLog')

    time = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), related_name='logins')
    mac_address = MACAddressField(null=True, integer=False)
    ip = models.GenericIPAddressField()
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

    @classmethod
    def log(cls, request: HttpRequest,
            user: Union[User, str], mac_address: Optional[MACAddress] = None,
            logged_in: bool = False, mac_updated: bool = False):
        """
        :param request: the request
        :param user: the user trying to login
        :param logged_in: did the user have the correct password?
        :param mac_updated: did the user successfully update their mac address?
        :param mac_address: what is the user's mac address at time of login?
        """
        if isinstance(user, str):
            qs = User.objects.filter(username__exact=user)
            if not qs.exists():
                return False
            user = qs.first()

        try:
            # TODO: Fill in host
            client_ip, is_routable = get_client_ip(request)
            cls._logger.info(f'Login: {user.username} from {client_ip} using {mac_address}. '
                             f'Success: {logged_in}, Updated: {mac_updated}')
            cls.objects.create(user=user,
                               mac_address=str(mac_address),
                               ip=client_ip,
                               host='',
                               logged_in=logged_in,
                               mac_updated=mac_updated)
        except Exception as err:
            cls._logger.error(err)

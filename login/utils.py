import logging
import random
import re
import time
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from ipware import get_client_ip
from netaddr import EUI, IPNetwork
from django.db.utils import OperationalError

from .models import Permissions


class MACAddress(EUI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def is_locally_administered(self):
        """
        Returns true if bit 1 of the 1st octet is set, indicating a locally administered MAC address.
        Returns false otherwise, indicating a globally unique (OUI enforced) MAC address.
        """
        return self.words[0] & 0x2


def restricted_network(view):
    def wrapper(request: HttpRequest, *args, **kwargs):
        try:
            netwk = Permissions.objects.get_raw_nodes('global/loginIPRestriction').first().value
        except OperationalError:
            netwk = IPNetwork('0.0.0.0/0')

        client_ip, routable = get_client_ip(request)
        if not settings.DEBUG and client_ip not in netwk:
            return redirect(f'{reverse("error")}?reason=wrongNetwork')

        return view(request, *args, **kwargs)
    return wrapper


def attach_mac_to_session(view):
    def wrapper(request: HttpRequest, *args, **kwargs):
        """Finds the dnsmasq lease file and matches the client IP to the responding MAC Address."""

        # TODO: Remove reliance on dnsmasq running on same server??

        def get_mac(ip: str) -> MACAddress:
            if (lease_file := Path('/var/lib/misc/dnsmasq.leases')).is_file():
                with open(lease_file) as fp:
                    for cnt, line in enumerate(fp):
                        line = line.strip().split(maxsplit=4)
                        if line[2] == ip:
                            return MACAddress(line[1])

        start = time.perf_counter()
        client_ip, routable = get_client_ip(request)
        macaddr: Optional[MACAddress] = get_mac(client_ip)
        logging.getLogger('Attach').info(f'Attaching MAC {macaddr} '
                                         f'to IP {client_ip} '
                                         f'in {(time.perf_counter() - start)*1000:.2f} ms')

        # Localhost Testing: Use semi-random MAC
        if macaddr is None and settings.DEBUG:
            macaddr = MACAddress(f'00ffff-{random.randrange(16 ** 6):06x}')

        request.session['mac_address'] = macaddr
        return view(request, *args, **kwargs)

    return wrapper


def check_mac_redirect(view):
    def wrapper(request: HttpRequest, *args, **kwargs):
        macaddr = request.session['mac_address']

        if macaddr is None:
            return redirect(f'{reverse("error")}?reason=unknownMAC')
        if macaddr.is_locally_administered:
            return redirect(reverse('instructions'))

        return view(request, *args, **kwargs)
    return wrapper


def mutually_exclusive(keyword, *keywords):
    keywords = (keyword,) + keywords

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if sum(k in keywords for k in kwargs) != 1:
                raise TypeError('You must specify exactly one of {}'.format(', '.join(keywords)))
            return func(*args, **kwargs)
        return inner
    return wrapper

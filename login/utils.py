from functools import wraps
from pathlib import Path
from typing import Union, Optional
from urllib.parse import quote

from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from ipware import get_client_ip
from netaddr import IPNetwork, EUI


class MacAddr:
    @classmethod
    def deserialize_from(cls, request: HttpRequest) -> Optional[EUI]:
        return EUI(request.session['macaddr']) if request.session.get('macaddr') is not None else None

    @classmethod
    def serialize_to(cls, request: HttpRequest, mac: Union[EUI, str, int, None]) -> None:
        if isinstance(mac, EUI):
            request.session['macaddr'] = mac.value
        elif isinstance(mac, str):
            request.session['macaddr'] = EUI(mac).value
        else:   # None / int
            request.session['macaddr'] = mac

    @classmethod
    def is_locally_administered(cls, mac: EUI) -> bool:
        """Returns true if bit 1 of the 1st octet is set, indicating a locally administered MAC address.
        Returns false otherwise, indicating a globally unique (OUI enforced) MAC address."""
        return mac.words[0] & 0x2


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


def attach_mac_to_session(view):
    def wrapper(request: HttpRequest, *args, **kwargs):
        lease_file = Path('/var/lib/misc/dnsmasq.leases')
        mac_addr = None
        if lease_file.is_file():
            with open(lease_file) as fp:
                for cnt, line in enumerate(fp):
                    l = line.strip().split(maxsplit=4)
                    if l[2] == get_client_ip(request)[0]:
                        mac_addr = l[1]
        if (mac_addr is not None) or (settings.DEBUG and mac_addr is None):
            MacAddr.serialize_to(request, mac_addr)
            # Hardcoded localhost testing
            MacAddr.serialize_to(request, 'ac-bb-cc-dd-ee-ff')
        else:
            return redirect(reverse('error') + f'?error={quote("Unable to determine MAC address of this device.")}')
        return view(request, *args, **kwargs)
    return wrapper


def restrict_to(range: IPNetwork):
    def decorator(view):
        def wrapper(request: HttpRequest, *args, **kwargs):
            client_ip, routable = get_client_ip(request)
            if not settings.DEBUG and client_ip not in range:
                return redirect(reverse('error') + f'?error={quote("Connecting from wrong network.")}')
            return view(request, *args, **kwargs)
        return wrapper
    return decorator

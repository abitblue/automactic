from functools import wraps
from pathlib import Path
from typing import Union, Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponseForbidden
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
        MacAddr.serialize_to(request, None)
        if lease_file.is_file():
            with open(lease_file) as fp:
                for cnt, line in enumerate(fp):
                    l = line.strip().split(maxsplit=4)
                    if l[2] == get_client_ip(request)[0]:
                        MacAddr.serialize_to(request, l[1])
        # Hardcoded localhost testing
        #MacAddr.serialize_to(request, 'aa-bb-cc-dd-ee-ff')
        return view(request, *args, **kwargs)
    return wrapper


def restrict_to(range: IPNetwork):
    def decorator(view):
        def wrapper(request: HttpRequest, *args, **kwargs):
            client_ip, routable = get_client_ip(request)
            if not settings.DEBUG and client_ip not in range:
                return HttpResponseForbidden('Connecting from wrong network.')
            return view(request, *args, **kwargs)
        return wrapper
    return decorator

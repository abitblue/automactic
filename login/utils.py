from functools import wraps
from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponseForbidden
from ipware import get_client_ip
from netaddr import IPNetwork, EUI


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
        request.session['macaddr'] = None
        if lease_file.is_file():
            with open(lease_file) as fp:
                for cnt, line in enumerate(fp):
                    l = line.strip().split(maxsplit=4)
                    if l[2] == get_client_ip(request)[0]:
                        request.session['macaddr'] = EUI(l[1])
        return view(request, *args, **kwargs)
    return wrapper


def is_locally_administered(mac: EUI) -> bool:
    """Returns true if bit 1 of the 1st octet is set, indicating a locally administered MAC address.
    Returns false otherwise, indicating a globally unique (OUI enforced) MAC address."""
    return mac.words[0] & 0x2


def restrict_to(range: IPNetwork):
    def decorator(view):
        def wrapper(request: HttpRequest, *args, **kwargs):
            client_ip, routable = get_client_ip(request)
            if not settings.DEBUG and client_ip not in range:
                return HttpResponseForbidden('Connecting from wrong network.')
            return view(request, *args, **kwargs)
        return wrapper
    return decorator

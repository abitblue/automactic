import os
from functools import wraps
from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponseForbidden
from ipware import get_client_ip
from netaddr import IPNetwork

from interface.cppm_api import CppmApi


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
        if lease_file.is_file():
            with open(lease_file) as fp:
                for cnt, line in enumerate(fp):
                    l = line.strip().split(maxsplit=4)
                    if l[2] == get_client_ip(request)[0]:
                        request.session['macaddr'] = l[1]
        else:
            request.session['macaddr'] = None
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

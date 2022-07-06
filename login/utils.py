from pathlib import Path
from typing import Optional
from urllib.parse import quote

from django.http import HttpRequest, HttpResponse
from django.conf import settings
from ipware import get_client_ip
from netaddr import EUI

class MacAddr:
    @classmethod
    def deserialize_from(cls, request: HttpRequest) -> Optional[EUI]:
        """Pulls mac-address data from the metadata of the request.
                EUI is used to ensure Mac-address is formatted correctly"""
        if request.session.get('macaddr') is not None:
            return EUI(request.session['macaddr'])
        else:
            return None

    @classmethod
    def locally_administered(cls, mac: EUI) -> bool:
        """Returns true if bit 1 of the 1st octet is set, indicating a locally administered MAC address.
                Returns false otherwise, indicating a globally unique (OUI enforced) MAC address."""
        return mac.words[0] & 0x2


def attach_mac_to_session(view):
    def wrapper(request: HttpRequest, *args, **kwargs):
        lease_file = Path('./var/lib/misc/dnsmasq.leases')
        mac_addr = None
        if lease_file.is_file():
            with open(lease_file) as fp:
                for cnt, line in enumerate(fp):
                    l = line.strip().split(maxsplit=4)
                    if l[2] == get_client_ip(request)[0]:
                        mac_addr = l[1]

        if mac_addr is not None:
            MacAddr.serialize_to(request, mac_addr)

        # Hardcoded localhost testing
        elif mac_addr is None and settings.DEBUG:
            MacAddr.serialize_to(request, 'ac-bb-cc-dd-ee-ff')
        else:
            return HttpResponse("UH OH???")
        return view(request, *args, **kwargs)
    return wrapper


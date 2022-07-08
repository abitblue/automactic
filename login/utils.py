from pathlib import Path
from typing import Optional, Union

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
    def serialize_to(cls, request: HttpRequest, mac: Union[EUI, str, int, None]) -> None:
        if isinstance(mac, EUI):
            request.session['macaddr'] = mac.value
        elif isinstance(mac, str):
            request.session['macaddr'] = EUI(mac).value
        else:  # None / int
            request.session['macaddr'] = mac

    @classmethod
    def locally_administered(cls, mac: EUI) -> bool:
        """Returns true if bit 1 of the 1st octet is set, indicating a locally administered MAC address.
                Returns false otherwise, indicating a globally unique (OUI enforced) MAC address."""
        return mac.words[0] & 0x2


def attach_mac_to_session(view):
    def wrapper(request: HttpRequest, *args, **kwargs):

        # TODO: Changing this probably
        """Finds the dnsmasq lease file and matches the client IP to the responding MAC Address."""
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
            MacAddr.serialize_to(request, 'aa-bb-cc-dd-ee-ff')
        else:
            # TODO: Return an actual response (AKA: Redirect)
            return HttpResponse("UH OH???")
        return view(request, *args, **kwargs)
    return wrapper


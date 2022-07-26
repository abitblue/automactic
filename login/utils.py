import random
from pathlib import Path
from typing import Optional, Union

from django.http import HttpRequest, HttpResponse
from django.conf import settings
from ipware import get_client_ip
from netaddr import EUI


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


def attach_mac_to_session(view):
    def wrapper(request: HttpRequest, *args, **kwargs):
        """Finds the dnsmasq lease file and matches the client IP to the responding MAC Address."""
        # TODO: Remove reliance on dnsmasq running on same server??

        def get_mac(ip: str) -> MACAddress:
            if (lease_file := Path('./var/lib/misc/dnsmasq.leases')).is_file():
                with open(lease_file) as fp:
                    for cnt, line in enumerate(fp):
                        line = line.strip().split(maxsplit=4)
                        if line[2] == ip:
                            return MACAddress(line[1])

        client_ip, routable = get_client_ip(request)
        macaddr: Optional[MACAddress] = get_mac(client_ip)
        request.session['mac_address'] = macaddr

        # Localhost Testing: Use semi-random MAC
        if macaddr is None and settings.DEBUG:
            request.session['mac_address'] = MACAddress(f'ffffff-{random.randrange(16**6):06x}')

        return view(request, *args, **kwargs)
    return wrapper


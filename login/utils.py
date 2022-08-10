import random
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from django.core.exceptions import ValidationError
from django.http import HttpRequest
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


class WhenType:
    _validator = re.compile(r'^(0[1-9]|1[012]|[+-]\d+?)/(0[1-9]|[12][0-9]|3[01]|[+-]\d+?)/(\d{4}|[+-]\d+?)$')

    def __init__(self, offset_str: str):
        self._offset_str = offset_str
        self._matched = self._validator.match(offset_str)
        if not self._matched:
            raise ValidationError(f"Invalid schema: {offset_str}")

    def as_datetime(self, reftime=None) -> datetime:
        if reftime is None:
            reftime = datetime.today()

        # Evaluate each group to form the date
        m, d, y = tuple(map(lambda ofst, ref: ref + eval(ofst) if ofst[0] in '+-' else int(ofst),
                            self._matched.groups(),
                            (reftime.month, reftime.day, reftime.year)
                            ))

        return datetime(y, m, d, tzinfo=timezone.utc)

    def __str__(self):
        return self._offset_str


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
            request.session['mac_address'] = MACAddress(f'00ffff-{random.randrange(16 ** 6):06x}')

        return view(request, *args, **kwargs)

    return wrapper

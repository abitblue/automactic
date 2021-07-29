from typing import Optional

from django.http import HttpRequest
from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.views import View
from netaddr import EUI

from login.utils import attach_mac_to_session, MacAddr


class Index(View):
    """Dispatches user to the login page or the instructions-to-disable-MAC-randomization page"""

    @method_decorator(attach_mac_to_session)
    def get(self, request: HttpRequest, *args, **kwargs):
        macaddr: Optional[EUI] = MacAddr.deserialize_from(request)

        if macaddr is None or not MacAddr.is_locally_administered(macaddr):
            return redirect(reverse('login'))
        else:
            return redirect(reverse('instructions'))


class Instructions(View):
    template_name = 'instructions.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        device_os = request.GET.get('os', None)
        versioncheck = request.GET.get('versioncheck', None)

        if versioncheck not in ['left', 'right', None]:
            return redirect(reverse('instructions'))

        verbose_os_name_nodefault = {
            'windows': 'Versions below Windows 10 do not',
            'mac': 'macOS does not',
            'android': 'Versions below Android 10 do not',
            'ios': 'Versions below iOS/iPadOS 14 do not',
        }.get(device_os, 'Your device does not')

        return render(request, self.template_name, {
            'device_os': device_os,
            'version_check': versioncheck,
            'verbose_os_name_nodefault': verbose_os_name_nodefault
        })

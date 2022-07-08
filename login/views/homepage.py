from typing import Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator

from login.utils import attach_mac_to_session, MacAddr
from netaddr import EUI

class Index(View):
    """Dispatches user to the login page or the instructions-to-disable-MAC-randomization page"""

    @method_decorator(attach_mac_to_session)
    def get(self, request: HttpRequest):
        macaddr: Optional[EUI] = MacAddr.deserialize_from(request)

        if macaddr is None or not MacAddr.locally_administered(macaddr):
            return HttpResponse('REDIRECT TO UNKNOWN MAC ERROR PAGE')
        else:
            return HttpResponse('REDIRECT TO INSTRUCTIONS')


class Instructions(View):
    """If the user is using randomized MAC addresses, these instructions will direct them to disable it"""
    template_name = 'instructions/with_os.html'

    def get(self, request: HttpRequest):
        device_os = request.GET.get('os', None)
        version_check = request.GET.get('version_check', None)

        # If device_os is not a GET parameter, ask user which OS is in use.
        # OR, if
        if not device_os:
            return render(request, 'login/instructions/without_os.html')

        return render(request, 'login/instructions/with_os.html', {
            'device_os': device_os,
            'version_check': version_check,
            'device_os_verbose': {
                'windows': 'Windows',
                'mac': 'macOS',
                'android': 'Android',
                'ios': 'iOS/iPadOS',
            }.get(device_os, 'Unknown')
        })

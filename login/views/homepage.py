from typing import Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator

# from login.forms.userLogin import UserLoginForm
from login.models import LoginHistory
from login.utils import attach_mac_to_session, MACAddress


@method_decorator(attach_mac_to_session, name='dispatch')
class Index(View):
    """Dispatches user to the instructions page, or shows the login page"""
    template_name = 'login/selection.html'

    def dispatch(self, request, *args, **kwargs):
        addr: Optional[MACAddress] = request.session.get('mac_address')

        if addr is None:
            return redirect(f'{reverse("error")}?reason=unknownMAC')

        if addr.is_locally_administered:
            return redirect(reverse('instructions'))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest):
        return render(request, self.template_name)


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

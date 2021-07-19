from typing import Optional

from django.http import HttpRequest
from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.views import View
from netaddr import EUI

from login.utils import attach_mac_to_session, is_locally_administered


class Index(View):
    """Dispatches user to the login page or the instructions-to-disable-MAC-randomization page"""

    @method_decorator(attach_mac_to_session)
    def get(self, request: HttpRequest, *args, **kwargs):
        macaddr: Optional[EUI] = request.session['macaddr']

        if macaddr is None or is_locally_administered(macaddr):
            return redirect(reverse('login'))
        else:
            return redirect(reverse('instructions'))


class Instructions(View):
    template_name = 'instructions.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        device_os = request.GET.get('os', None)

        if device_os is None:
            return render(request, self.template_name)

        return render(request, self.template_name, {
            'device_os': device_os,
        })

from typing import Optional

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import HttpRequest, HttpResponse

from login.forms import UserLoginForm
from login.utils import MACAddress


class Login(View):
    def dispatch(self, request, *args, **kwargs):
        addr: Optional[MACAddress] = request.session.get('mac_address')

        if addr is None:
            return redirect(f'{reverse("error")}?reason=unknownMAC')
        if addr.is_locally_administered:
            return redirect(reverse('instructions'))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, usertype: str, *args, **kwargs):
        help_template = {
            'student': f"login/batch/students.html",
            'teacher': f"login/batch/teachers.html",
            'guest': f"login/batch/guest.html"
        }

        return render(request, f'login/login.html', {
            'usertype': usertype,
            'help_template': help_template[usertype],
            'form': UserLoginForm(user_type=usertype),
        })

    def post(self, request: HttpRequest, usertype: str, *arg, **kwargs):
        form = UserLoginForm(request=request, user_type=usertype, data=request.POST)
        mac_addr: MACAddress = request.session['mac_address']

        # Rate limit first. Log once possible. try/except/finally?

        # Check if username exists on Clearpass
        # Check if MAC Address already exists on Clearpass

        # If username does not exist, add device.

        # If username exists, count number of device they have. Compare against permissions.
        # If exceeding, then block.
        # If not exceeding, replace the oldest device.
        # TODO: Select which old device

        # Attempt to change on Clearpass, show error to user if error. Else show success page.


        return HttpResponse('test!')

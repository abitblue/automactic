from typing import Optional

from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import HttpRequest, HttpResponse
from netaddr import EUI

from login.forms import UserLoginForm
from login.models import LoginHistory, User
from login.utils import MACAddress
import interface.api as api


access = api.Token()


class Login(View):
    help_template = {
        'student': f"login/batch/students.html",
        'teacher': f"login/batch/teachers.html",
        'guest': f"login/batch/guest.html"
    }

    def dispatch(self, request, *args, **kwargs):
        addr: Optional[MACAddress] = request.session.get('mac_address')

        if addr is None:
            return redirect(f'{reverse("error")}?reason=unknownMAC')
        if addr.is_locally_administered:
            return redirect(reverse('instructions'))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, usertype: str, *args, **kwargs):

        return render(request, f'login/login.html', {
            'usertype': usertype,
            'help_template': self.help_template[usertype],
            'form': UserLoginForm(user_type=usertype),
        })

    def post(self, request: HttpRequest, usertype: str, *arg, **kwargs):
        form = UserLoginForm(request=request, user_type=usertype, data=request.POST)
        mac_addr: MACAddress = request.session['mac_address']

        if not form.is_valid():
            LoginHistory.log(request=request, user=form.cleaned_data.get('username'), logged_in=form.password_correct, mac_address=mac_addr)
            print(mac_addr)
            return render(request, 'login/login.html', {'usertype': usertype, 'help_template': self.help_template[usertype], 'form': form})

        resp = access.get_device(mac=mac_addr)
        print(resp)

        if resp is not None:
            LoginHistory.log(request=request, user=form.cleaned_data.get('username'), logged_in=form.password_correct)
            return redirect(reverse('error') + '?reason=alreadyRegistered')

        name = ""
        user = form.user_cache
        usertype = str(usertype).lower()
        device_name = form.cleaned_data.get('device_name')

        if usertype == 'guest':
            name = f'G:{user.device_modified_count}'
        elif usertype == 'student':
            name = f'S:{user.username}'
        elif usertype == 'staff':
            name = f'T:{user.username}'

        resp_user = access.get_device(name=name)
        if resp_user is not None:
            if len(resp_user.device) >= User.objects.get(username=user).get_permission('deviceLimit'):
                resp_user.device.sort(key=lambda x: x['start_time'])
                access.update_device(device_id=resp_user.device[0]['id'], updated_fields={
                    'mac': str(mac_addr),
                    'device_name': device_name,
                })
                # TODO: log
                return HttpResponse("yes2")

        expire_time = User.objects.get(username=user).get_permission('expireTime', default=None)
        access.add_device(mac=mac_addr, username=name, device_name=device_name, time=expire_time)
        LoginHistory.log(request=request, user=form.cleaned_data.get('username'), logged_in=form.password_correct,
                         mac_address=mac_addr)

        return HttpResponse("yes")
        # If username does not exist, add device.

        # If username exists, count number of device they have. Compare against permissions.
        # If exceeding, then block.
        # If not exceeding, replace the oldest device.
        # TODO: Select which old device

        # Attempt to change on Clearpass, show error to user if error. Else show success page.




from typing import Optional

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import HttpRequest

from login.forms import UserLoginForm
from login.models import LoginHistory
from login.utils import MACAddress
import interface.api as api

# TODO: Show error if clearpass errors
# TODO: Ability to select which device to replace if more than 1 device allowed.

access = api.Token()


class Login(View):
    template_name = 'login/login.html'
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
        # Check if this device is already registered. If it is, then redirect to an instructions page.
        if access.get_device(mac=request.session['mac_address']) is not None:
            return redirect(f'{reverse("error")}?reason=alreadyRegistered')

        return render(request, self.template_name, {
            'usertype': usertype,
            'help_template': self.help_template[usertype],
            'form': UserLoginForm(user_type=usertype),
        })

    def post(self, request: HttpRequest, usertype: str, *args, **kwargs):
        form = UserLoginForm(request=request, user_type=usertype, data=request.POST)
        mac_addr: MACAddress = request.session['mac_address']

        # Check whether the user has the correct password or is being rate limited
        if not form.is_valid():
            LoginHistory.log(request=request, user=form.cleaned_data.get('username'), mac_address=mac_addr,
                             logged_in=form.password_correct)
            return render(request, self.template_name, {
                'usertype': usertype,
                'help_template': self.help_template[usertype],
                'form': form
            })

        # Grab Data
        user = form.user_cache
        device_name = form.cleaned_data.get('device_name')
        clearpass_name = '{}:{}'.format(
            {
                'guest': 'G',
                'student': 'S',
                'staff': 'T'
            }[str(usertype).lower()],
            user.username
        )

        # Check how many devices the user has. If it exceeds how many they should have, replace the earliest device.
        clearpass_user = access.get_device(name=clearpass_name)
        if clearpass_user is not None:
            if len(clearpass_user.device) >= user.get_permission('deviceLimit'):
                clearpass_user.device.sort(key=lambda x: x['start_time'])
                access.update_device(device_id=clearpass_user.device[0]['id'], updated_fields={
                    'mac': str(mac_addr),
                    'device_name': device_name,
                })
                LoginHistory.log(request=request, user=user, mac_address=mac_addr, logged_in=True, mac_updated=True)
                return redirect(reverse('success'))

        # TODO: Handle 0 devices allowed.

        # If the user does not exist, create a new device, following the expireTime rules.
        expire_time = user.get_permission('expireTime', default=None)
        access.add_device(mac=mac_addr, username=clearpass_name, device_name=device_name, time=expire_time)
        LoginHistory.log(request=request, user=user, mac_address=mac_addr, logged_in=True, mac_updated=True)

        return redirect(reverse('success'))

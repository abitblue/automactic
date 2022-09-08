import datetime
from typing import Optional, TYPE_CHECKING

from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import HttpRequest
from django.utils import timezone
from django.utils.decorators import method_decorator

from login.forms import UserLoginForm
from login.models import LoginHistory
from login.utils import MACAddress, restricted_network, check_mac_redirect
import interface.api as api

if TYPE_CHECKING:
    from login.models.permissions import WhenType
    from login.models import User

# TODO: Show error if clearpass errors
# TODO: Ability to select which device to replace if more than 1 device allowed.

access = api.Token()


@method_decorator([restricted_network, check_mac_redirect], name='dispatch')
class Login(View):
    template_name = 'login/login.html'
    help_template = {
        'student': f"login/batch/student.html",
        'faculty': f"login/batch/faculty.html",
        'guest': f"login/batch/guest.html"
    }

    def get(self, request: HttpRequest, usertype: str, *args, **kwargs):
        # Check if this device is already registered. If it is, then redirect to an instructions page.
        if not settings.DEBUG and access.get_device(mac=request.session['mac_address']).status_code != 404:
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
        user: User = form.user_cache
        device_name = form.cleaned_data.get('device_name')

        # Save last login data
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        result = None

        # Check how many devices the user has. If it exceeds how many they should have, replace the earliest device.
        if (device_limit := user.get_permission('deviceLimit')) == 0:
            return redirect(f'{reverse("error")}?reason=restricted')

        elif device_limit is not None:
            clearpass_user = access.get_device(username=user.clearpass_name)
            if clearpass_user is not None and len(clearpass_user.device) >= device_limit:
                clearpass_user.device.sort(key=lambda x: x['start_time'])
                result = access.update_device(device_id=clearpass_user.device[0]['id'], updated_fields={
                    'mac': str(mac_addr),
                    'notes': device_name,
                })

        else:
            # If the user does not exist, or if limit not exceeded, create a new device, following the expireTime rules
            when: WhenType = user.get_permission('expireTime', default=None)
            expire_time: Optional[datetime] = when.as_datetime(timezone.now()) if when is not None else None
            result = access.add_device(mac=mac_addr, username=user.clearpass_name, device_name=device_name, time=expire_time)

        # Check result status and show user success or API error page
        if result and str(result.status_code)[0] == '2':
            user.mac_modifications += 1
            user.save(update_fields=["mac_modifications"])
            LoginHistory.log(request=request, user=user, mac_address=mac_addr, logged_in=True, mac_updated=True)
            return redirect(reverse('success'))

        LoginHistory.log(request=request, user=user, mac_address=mac_addr, logged_in=True, mac_updated=False)
        return redirect(f'{reverse("error")}?reason=clearpassAPI')

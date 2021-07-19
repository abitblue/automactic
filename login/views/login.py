import logging
import smtplib
from datetime import timedelta
from urllib.parse import quote

from django.core.mail import send_mail
from django.http import HttpRequest
from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from netaddr import IPNetwork

from automactic.settings import EMAIL_RECIPIENTS
from interface.cppm_api import CppmApiException
from login.forms import IndexAuthenticationForm
from login.models import LoginHistory, User, UserType
from login.utils import restrict_to, attach_mac_to_session
from interface.cppm_iface import Clearpass


logger = logging.getLogger('views.login')

@method_decorator(restrict_to(IPNetwork('192.168.0.0/16')), name='dispatch')
class Login(View):
    template_name = 'login.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.template_name, {'form': IndexAuthenticationForm()})

    @method_decorator(attach_mac_to_session)
    def post(self, request: HttpRequest, *args, **kwargs):
        form = IndexAuthenticationForm(request, data=request.POST)
        if not form.is_valid():
            LoginHistory.log(user=form.cleaned_data.get('username'), logged_in=form.password_correct)
            return render(request, self.template_name, {'form': form})

        # Clearpass:
        # Check for devices with the name start with "S:{OSIS}:"/"T:{email}:"/"G:{123}:" and sponsor profile oauth2:automactic

        # If not student or count == 0:
        # create new device
        # else: (is student and count > 0) replace old device with new one

        # If error, show error to user
        # Else, show success page

        name = ""
        user = form.user_cache
        user_type = str(user.type).lower()
        if user_type == 'guest':
            # UserCache will be guest account
            name = f'G:{user.device_modified_count}'
        elif user_type == 'student':
            name = f'S:{user.username}'
        elif user_type == 'staff':
            name = f'T:{user.username}'

        mac_addr = request.session['macaddr']
        device_name = form.cleaned_data.get('device_name')
        registered = Clearpass.get_device(name=name, additional_filers={'sponsor_name': 'oauth2:automactic'})

        def run_cppm_cmd(func, *args, **kwargs):
            try:
                func(*args, **kwargs)
                user.device_modified_count += 1
                user.save()

                if user.device_modified_warning_count is not None and user.device_modified_count >= user.device_modified_warning_count:
                    try:
                        msg = f'This is an automated message.\n\nThe user: {user} has registered {user.device_modified_count} devices.' \
                              f'This email triggers after f{user.device_modified_count} registrations.' \
                              f'Please check login history for any suspicious activity. ' \
                              f'If none can be found, you may reset the modified count using the administrative actions.'
                        send_mail('[automactic] Warning: Possible suspicious activity in user device registrations', msg,
                                  None, EMAIL_RECIPIENTS)
                    except smtplib.SMTPException as err:
                        logger.error(err)

                LoginHistory.log(user=form.cleaned_data.get('username'), logged_in=form.password_correct,
                                 mac_address=mac_addr)
                return redirect(reverse('success'))
            except CppmApiException as err:
                LoginHistory.log(user=form.cleaned_data.get('username'), logged_in=form.password_correct)
                return redirect(reverse('error') + f'?error={quote(str(err))}')

        if user_type != 'student' or registered['count'] == 0:
            exp_time = 0
            if user.device_validity_period is not None:
                exp_time = timezone.now() + user.device_validity_period
            return run_cppm_cmd(Clearpass.create_device, name=name, mac=mac_addr,
                                notes=form.cleaned_data.get('device_name'), expire_time=exp_time)

        else:
            return run_cppm_cmd(Clearpass.update_device, device_id=int(registered['items'][0]['id']),
                                data={'notes': device_name, 'mac': mac_addr})

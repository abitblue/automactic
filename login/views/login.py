from django.http import HttpRequest
from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.views import View
from netaddr import IPNetwork

from login.forms import IndexAuthenticationForm
from login.models import LoginHistory
from login.utils import restrict_to, attach_mac_to_session


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

        # If no devices exist or limitless account:
            # create new device
        # else: (devices exist and not limitless acct)
            # if limit == 1, replace old device with new one
            # elif limit > 1, ask which devices to revoke, if any, and enforce limit if limit reached
            # else (limit < 1), error, cannot register any devices

        # Construct search

        # If error, show error to user
        # Else, show success page

        # Temporary:
        return redirect(reverse('error') + '?error=success')

from datetime import timedelta

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from interface.rotating_passwd import RotatingCode
from login.models import LoginHistory, User


class IndexAuthenticationForm(AuthenticationForm):
    device_name = forms.CharField(label='',
                                  required=False,
                                  widget=forms.TextInput(attrs={'maxlength': 40, 'placeholder': 'Device Name'}))

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].label = ''
        self.fields['password'].label = ''
        self.fields['username'].widget.attrs['placeholder'] = 'ID *'
        self.fields['password'].widget.attrs['placeholder'] = 'Token *'
        self.password_correct = False

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': "Incorrect username and/or password",
        'rate_limit': 'Too many attempts. Please try again tomorrow.',
        'mac_missing': 'Unable to determine the MAC address of this device'
    }

    def rate_limit_check(self, user):
        if user.bypass_rate_limit:
            return

        # Rate Limit - Preventing abuse (rapidly changing devices) and account brute-forcing
        # Always rate limit if 5 incorrect passwords in an hour
        # No other limit on first 3 successful modifications
        # After that, rate limit to 5 modifications per hour and one unique mac address per 18 hours
        not_new_user = LoginHistory.objects.filter(user=user, mac_address__isnull=False).count() > 3
        passwd_per_hour_limit = LoginHistory.objects.filter(user=user, logged_in=False,
                                                            time__gt=timezone.now() - timedelta(
                                                                hours=1)).count() > 5
        modifications_limit = LoginHistory.objects.filter(user=user, mac_address__isnull=False,
                                                          time__gt=timezone.now() - timedelta(hours=1)).count() > 5
        unique_mac_limit = LoginHistory.objects.filter(user=user, mac_address=self.request.session.get('macaddr'),
                                                       time__gt=timezone.now() - timedelta(hours=18)).exists()

        if passwd_per_hour_limit or (not_new_user and (modifications_limit or unique_mac_limit)):
            raise ValidationError(
                self.error_messages['rate_limit'],
                code='rate_limit',
            )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        # Early exit if MAC address not present.
        if self.request.session.get('macaddr') is None:
            raise ValidationError(
                self.error_messages['mac_missing'],
                code='mac_missing',
            )

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)

            if username == 'guest' and RotatingCode.verify(password):
                self.user_cache = User.objects.get(username__exact='guest')

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.password_correct = True
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        self.rate_limit_check(user)

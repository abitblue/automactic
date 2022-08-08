import re
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm

from login.models import User, LoginHistory

# TODO: Update Last Login!!!

class UserLoginForm(BaseAuthenticationForm):
    device_name = forms.CharField(label='', required=False,
                                  widget=forms.TextInput(attrs={
                                      'maxlength': 40,
                                      'placeholder': 'Device Name'
                                  }))

    def __init__(self, user_type: str, request=None, *args, **kwargs):
        widget_placeholders = {
            'student': ('OSIS *', 'DOB (MMDDYYYY) * '),
            'teacher': ('Email (jdoe1@schools.nyc.gov) *', 'Password *'),
            'guest': ('Username *', 'Token *'),
        }

        super().__init__(request, *args, **kwargs)
        self.fields['username'].label = ''
        self.fields['password'].label = ''
        self.fields['username'].widget.attrs['placeholder'] = widget_placeholders[user_type][0]
        self.fields['password'].widget.attrs['placeholder'] = widget_placeholders[user_type][1]
        self.password_correct = False
        self.mac_changed = False

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'formField'

    whitespace_regex = re.compile(r'\s+')
    error_messages = {
        **BaseAuthenticationForm.error_messages,
        'invalid_login': "Incorrect username and/or password",
        'rate_limit': 'Too many attempts. Please try again later.',
        'mac_missing': 'Unable to determine the MAC address of this device',
    }

    def rate_limit_check(self, user: User):
        if user.get_permission('bypassRateLimit', default=False):
            return

        perms = {
            perms.suffix: perms.value
            for perms in User.objects.get(username=user).permissions().filter(suffix__startswith="rateLimit")
        }

        not_new_user = LoginHistory.objects.filter(user=user, mac_address__isnull=False).count() > perms.get(
            'rateLimit/modificationsUntilNotNewUser')

        password_per_hr_lim = LoginHistory.objects.filter(user=user, logged_in=False,
                                                          time__gt=timezone.now() - timedelta(
                                                              hours=1)).count() > perms.get(
            'rateLimit/passwordPerHourLimit')

        modification_lim = LoginHistory.objects.filter(user=user, logged_in=True, mac_updated=True,
                                                       time__gt=(timezone.now() - timedelta(
                                                           hours=1)).count() > perms.get(
                                                           'rateLimit/passwordPerHourLimit'))

        unique_mac_lim = LoginHistory.objects.filter(user=User, mac_address=self.request.session.get('macaddr'),
                                                     time__gt=timezone.now() - timedelta(perms.get("rateLimit/uniqueMACAddressInterval"))).exists()

        if password_per_hr_lim or (not_new_user and (modification_lim or unique_mac_lim)):
            raise ValidationError(
                    self.error_messages['rate_limit'],
                    code='rate_limit'
                )
        # Rate limits attempts to prevent abuse by rapidly changing devices, and account brute-forcing
        # Default Rate Limit Rules (modified in settings)
        # Always rate limit username if 5 incorrect passwords were inputted in an hour.
        # No other limit on first 3 successful modifications
        # After that, rate limit to 5 modifications per hour and one unique mac address every 18 hours
        return

    def confirm_login_allowed(self, user):
        # This is called by the super().clean() method.
        # By the time this is called, the password is indeed correct
        self.password_correct = True
        super().confirm_login_allowed(user)
        self.rate_limit_check(user)

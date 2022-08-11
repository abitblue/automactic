import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm

from login.models import User, UserType


class UserLoginForm(BaseAuthenticationForm):

    # device_name = forms.CharField(label='', required=False,
    #                               widget=forms.TextInput(attrs={
    #                                   'maxlength': 40,
    #                                   'placeholder': 'Device Name (Ex: Sussy\'s Phone 13)',
    #                               }))

    mac_address = forms.CharField(label='', required=True,
                                  widget=forms.TextInput(attrs={
                                      'maxlength': 17,
                                      'placeholder': 'Mac Address (Ex: C3:F6:3E:0F:56:13)',
                                  }))

    def __init__(self, user_type: str, request=None, *args, **kwargs):
        widget_placeholders = {
            'student': ('OSIS *', 'DOB (MMDDYYYY) * '),
            'teacher': ('Email (Ex: youweee@schools.nyc.gov) *', 'Mac Address *'),
            'guest': ('Username *', 'Token *'),
        }

        super().__init__(request, *args, **kwargs)
        self.fields['username'].label = ''
        self.fields['username'].widget.attrs['placeholder'] = widget_placeholders[user_type][0]
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

    

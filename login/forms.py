from datetime import timedelta

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UsernameField, ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import LoginHistory, User


class IndexAuthenticationForm(AuthenticationForm):
    device_name = forms.CharField(label='',
                                  required=False,
                                  widget=forms.TextInput(attrs={'maxlength': 40, 'placeholder': 'Device Name'}))

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].label = ''
        self.fields['password'].label = ''
        self.fields['username'].widget.attrs['placeholder'] = 'ID'
        self.fields['password'].widget.attrs['placeholder'] = 'Token'
        self.password_correct = False

    error_messages = {
        **AuthenticationForm.error_messages,
        'rate_limit': 'Too many login attempts. Please try again later.',
        'mac_missing': 'Unable to determine the MAC address of this device'
    }

    def confirm_login_allowed(self, user):
        # Early exit if MAC address not present.
        if self.request.session.get('macaddr') is None:
            raise ValidationError(
                self.error_messages['mac_missing'],
                code='mac_missing',
            )

        super().confirm_login_allowed(user)

        # We have the ability to login (passwd correct, active acct, mac present) by the time we reach here in the code
        # and can proceed to rate limiting
        self.password_correct = True

        if user.bypass_rate_limit:
            return

        # Rate Limit - Preventing abuse (rapidly changing devices) and account brute-forcing
        # Always rate limit if 5 incorrect passwords in an hour
        # No other limit on first 3 successful modifications
        # After that, rate limit to 5 modifications per hour and one unique mac address per 18 hours
        not_new_user = LoginHistory.objects.filter(user=user, mac_address__isnull=False).count() > 3
        passwd_per_hour_limit = LoginHistory.objects.filter(user=user, logged_in=False,
                                                            time__gt=timezone.now() - timedelta(hours=1)).count() > 5
        modifications_limit = LoginHistory.objects.filter(user=user, mac_address__isnull=False,
                                                          time__gt=timezone.now() - timedelta(hours=1)).count() > 5
        unique_mac_limit = LoginHistory.objects.filter(user=user, mac_address=self.request.session.get('macaddr'),
                                                       time__gt=timezone.now() - timedelta(hours=18)).exists()

        if passwd_per_hour_limit or (not_new_user and (modifications_limit or unique_mac_limit)):
            raise ValidationError(
                self.error_messages['rate_limit'],
                code='rate_limit',
            )


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label='Password confirmation',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text="Enter the same password as before, for verification."
    )

    error_messages = {
        'password_mismatch': 'The two password fields didn’t match.',
    }

    class Meta:
        model = User
        fields = ('username', 'type', 'is_staff', 'disable_on', 'device_limit', 'device_validity_period',
                  'device_modified_warning_count')
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs['autofocus'] = True

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text=
        'Raw passwords are not stored, so there is no way to see this '
        'user’s password, but you can change the password using '
        '<a href="../password/">this form</a>.'
    )

    class Meta:
        model = User
        fields = '__all__'
        field_classes = {'username': UsernameField}

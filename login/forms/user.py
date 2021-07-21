from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UsernameField, ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from login.models import User


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
        fields = ('username', 'type', 'is_staff', 'disable_on', '_device_validity_period',
                  '_device_modified_warning_count')
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

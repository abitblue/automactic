import csv
import io
import re

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UsernameField, ReadOnlyPasswordHashField
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db.models import Q

from login.models import User, UserType


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
        fields = ('username', 'type', 'is_staff', '_device_validity_period',
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


class UserBulkImportForm(forms.Form):
    CHOICES = [('replace', 'Replace'),
               ('insert', 'Insert')]

    #50 MB upload limit
    file = forms.FileField(label='File', help_text='Upload limit: 50MB', required=True)
    import_type = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, label='Type', required=True)

    osis_re = re.compile(r'^\d{9}$')
    date_re = re.compile(r'^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](\d{4})$')
    email_re = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    token_re = re.compile(r"^.{8,}$")

    error_messages = {
        'missing_type_header': 'File is missing a header or is not a CSV file',
        'invalid_data': 'Error in file on line {}: {}',
        'file_too_big': 'Uploaded file is too large'
    }

    def clean(self):
        if self.errors:
            return

        if self.cleaned_data.get('file').size > 52428800:
            raise ValidationError(self.error_messages['file_too_big'], code='file_too_big')

        self.validate_data()

    def validate_data(self, write=False):
        self.cleaned_data.get('file').seek(0)
        try:
            filedata = io.StringIO(self.cleaned_data.get('file').read().decode('utf-8'))
            data = csv.DictReader(filedata, delimiter=',')
            bulk_create_list = []

            for cnt, row in enumerate(data):
                if row['Type'].lower() == 'student':
                    osis_match, date_match = self.osis_re.match(row['OSIS']), self.date_re.match(row['DOB'])
                    if not (osis_match and date_match):
                        # cnt + 2 b/c +1 for 0 index and +1 for DictReader counting from line after header
                        raise ValidationError(
                            self.error_messages['invalid_data'].format(cnt + 2, f'"{row}" - OSIS or DOB invalid'),
                            code='invalid_data')

                    if write:
                        student_type = UserType.objects.get(name='Student')
                        osis, dob = osis_match.group(), ''.join(date_match.groups())
                        bulk_create_list.append(User(username=osis, type=student_type,
                                                     password=make_password(dob, None, 'plain')))

                # TODO: Other user types
                if row['Type'].lower() == 'staff':
                    email_match, token_match = self.email_re.match(row['Email']), self.token_re.match(row['Token'])
                    if not (email_match and token_match):
                        raise ValidationError(
                            self.error_messages['invalid_data'].format(cnt + 2, f'"{row}" - Email or Token invalid'),
                            code='invalid_data')

                    if write:
                        staff_type = UserType.objects.get(name='Staff')
                        email, token = email_match.group(0), token_match.group()
                        bulk_create_list.append(User(username=email, type=staff_type,
                                                     password=make_password(token, None, 'plain')))

            if write:
                if self.cleaned_data.get('import_type') == 'replace':
                    User.objects.all().exclude(Q(type__name='Sentinel') | Q(type__name='Guest')).delete()
                return len(User.objects.bulk_create(bulk_create_list, ignore_conflicts=True))

        except (csv.Error, ValueError) as err:
            raise ValidationError(self.error_messages['missing_type_header'], code='missing_type_header')

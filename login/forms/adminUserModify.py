import csv
import io
import logging
import re

from django import forms
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db.models import Q

from login.models import UserType, User


class UserBulkImportForm(forms.Form):
    _logger = logging.getLogger('BulkImportUsers')

    CHOICES = [('replace', 'Replace'),
               ('insert', 'Insert')]

    # 50 MB upload limit
    file = forms.FileField(label='File', help_text='Upload limit: 50MB', required=True)
    import_type = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, label='Type', required=True)

    error_messages = {
        'missing_type_header': 'File is missing a header or is not a CSV file',
        'invalid_data': 'Error in file on line {}: {}',
        'file_too_big': 'Uploaded file is too large'
    }

    osis_re = re.compile(r'^\d{9}$')
    date_re = re.compile(r'^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](\d{4})$')
    email_re = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    token_re = re.compile(r"^.{8,}$")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bulk_import_list = []

    def clean(self):
        if self.errors:
            return

        if self.cleaned_data.get('file').size > 52428800:
            raise ValidationError(self.error_messages['file_too_big'], code='file_too_big')

        self.validate_data()

    def _enumerate_csv(self):
        self.cleaned_data.get('file').seek(0)
        try:
            filedata = io.StringIO(self.cleaned_data.get('file').read().decode('utf-8'))
            data = csv.DictReader(filedata, delimiter=',')

            for cnt, row in enumerate(data):
                # cnt + 2:
                #   +1 for 1-indexing
                #   +1 for DictReader counting from line after header
                yield (cnt + 2, {
                    'type': row['Type'].lower(),
                    'username': row['Username'],
                    'token': row['Token'],
                })

        except csv.Error as err:
            raise ValidationError(self.error_messages['missing_type_header'], code='missing_type_header')

    def validate_data(self):
        self._bulk_import_list = []

        for lineno, item in self._enumerate_csv():
            match item['type']:
                case 'student':
                    osis_match, date_match = self.osis_re.match(item['username']), self.date_re.match(item['token'])
                    if not (osis_match and date_match):
                        raise ValidationError(
                            self.error_messages['invalid_data'].format(lineno, f'"{item}" - OSIS or DOB invalid'),
                            code='invalid_data')

                    osis, dob = osis_match.group(), ''.join(date_match.groups())
                    self._bulk_import_list.append(User(username=osis, type=UserType.objects.get(name='Student'),
                                                       password=make_password(dob, None, 'plain')))

                case 'staff':
                    email_match, token_match = self.osis_re.match(item['username']), self.date_re.match(item['token'])
                    if not (email_match and token_match):
                        raise ValidationError(
                            self.error_messages['invalid_data'].format(lineno, f'"{item}" - Email or Token invalid'),
                            code='invalid_data')

                    email, token = email_match.group(0), token_match.group()
                    self._bulk_import_list.append(User(username=email, type=UserType.objects.get(name='Staff'),
                                                       password=make_password(token, None, 'plain')))

                case _:
                    usertype = item['type']
                    raise ValidationError(self.error_messages['invalid_data'].format(lineno, f'"{usertype}" - Unknown type'))

    def write_data(self, validated=False):
        if not validated:
            self.validate_data()

        mode: str = self.cleaned_data.get('import_type')
        bulk_usernames = [user.username for user in self._bulk_import_list]
        self._logger.info(f"Importing Users: Mode: {mode} CSV Count: {len(self._bulk_import_list)}")

        num_updated = 0
        if mode == 'replace':
            # Bulk update `is_active=False` for all students and staff not in list and is not a superuser or guest acct
            num_updated = User.objects.all().exclude(
                Q(type__name='Superuser') | Q(type__name='Guest') | Q(username__in=bulk_usernames)
            ).update(is_active=False)

        # Replacing and Inserting:
        # Bulk create users. Ignore already existing ones. Set all of them to active=true.
        num_updated += User.objects.filter(username__in=bulk_usernames).update(is_active=True)
        objs_created = User.objects.bulk_create(self._bulk_import_list, ignore_conflicts=True)

        return len(objs_created)
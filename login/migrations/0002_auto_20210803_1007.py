# Generated by Django 3.2.6 on 2021-08-03 14:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='disable_on',
        ),
        migrations.RemoveField(
            model_name='usertype',
            name='disable_in',
        ),
    ]

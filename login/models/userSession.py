from django.contrib.sessions.models import Session
from django.db import models
from django.contrib.auth.signals import user_logged_in

from .user import User, get_sentinel_user


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    session_key = models.CharField(max_length=64)

    class Meta:
        verbose_name = 'User Type'

    def __str__(self):
        return f'Session {self.session_key} for {self.user}'

    @property
    def session(self):
        return Session.objects.filter(session_key__exact=self.session_key)


def user_logged_in_handler(sender, request, user, **kwargs):
    UserSession.objects.get_or_create(user=user, session_key=request.session.session_key)


user_logged_in.connect(user_logged_in_handler)

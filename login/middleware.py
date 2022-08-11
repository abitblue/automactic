from django.utils import timezone

from login.models import Permissions


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if local_tz := Permissions.objects.filter(permission='global/localTimezone').first():
            timezone.activate(local_tz.value)
        return self.get_response(request)

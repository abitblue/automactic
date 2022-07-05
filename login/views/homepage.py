from django.http import HttpRequest, HttpResponse
from django.views import View


class Index(View):
    """Dispatches user to the login page or the instructions-to-disable-MAC-randomization page"""

    def get(self, request: HttpRequest):
        # TODO: fill!
        return HttpResponse('test')

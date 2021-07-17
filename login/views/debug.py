import socket
from django.http import HttpRequest
from django.shortcuts import render
from django.views import View
from ipware import get_client_ip


class Debug(View):
    template_name = 'debug.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        def get_host_ip():
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # This grabs the default route
                retval = s.getsockname()[0]  # Get IP, not port as well
            return retval

        return render(request, self.template_name, {
            'data': {
                'Host': f'{get_host_ip()} ({socket.gethostname()})',
                'Client': get_client_ip(request)[0],
                'SessionKey': request.session.session_key,
                'SessionData': dict(request.session.items()),
            }
        })
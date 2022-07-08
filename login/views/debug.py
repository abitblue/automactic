import socket

from django.http import HttpRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.clickjacking import xframe_options_sameorigin
from ipware import get_client_ip
from netaddr import EUI


# Allow same origin loading for iframe
# https://docs.djangoproject.com/en/4.0/ref/clickjacking/#setting-x-frame-options-per-view
@method_decorator(xframe_options_sameorigin, name='dispatch')
class Debug(View):
    """Display debug info about the connection"""
    template_name = 'login/debug.html'

    def get(self, request: HttpRequest):
        def get_host_ip():
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # This grabs the default route
                retval = s.getsockname()[0]  # Get IP, not port as well
            return retval

        show_session_data: bool = bool(request.GET.get('showSessionData', False))
        mac_address: EUI = request.session.get('macaddr', None)
        client_ip, is_routable = get_client_ip(request)

        return render(request, self.template_name, {
            'data': {
                'Host': f'{get_host_ip()} ({socket.gethostname()})',
                'Client': client_ip,
                'SessionKey': request.session.session_key,
                **({'SessionData': dict(request.session.items())} if show_session_data else {}),
                # TODO: Add Mac Address to list
            }
        })

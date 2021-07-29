import socket
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.clickjacking import xframe_options_sameorigin
from ipware import get_client_ip

from login.utils import MacAddr


@method_decorator(xframe_options_sameorigin, name='dispatch')
class Debug(View):
    template_name = 'debug.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        def get_host_ip():
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # This grabs the default route
                retval = s.getsockname()[0]  # Get IP, not port as well
            return retval

        mac_addr = MacAddr.deserialize_from(request)
        showsessiondata = request.GET.get('showsessiondata', None)
        return render(request, self.template_name, {
            'data': {
                'Host': f'{get_host_ip()} ({socket.gethostname()})',
                'Client': get_client_ip(request)[0],
                'SessionKey': request.session.session_key,
                **({'SessionData': dict(request.session.items())} if showsessiondata else {}),
                'Mac Addr': f'{mac_addr} (OUI Enforced: {not MacAddr.is_locally_administered(mac_addr)})' if mac_addr is not None else 'N/A',
            }
        })

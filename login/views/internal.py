from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from interface.rotating_passwd import RotatingCode


@method_decorator(staff_member_required, name='dispatch')
class InternalGuestPasswd(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        return JsonResponse({
            'passwd': RotatingCode.get(),
            'expire': int(RotatingCode.remaining_time())
        })

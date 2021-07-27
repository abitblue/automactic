from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from admin.admin import admin_site
from interface.rotating_passwd import RotatingCode
from login.forms.user import UserBulkImportForm


@method_decorator(staff_member_required, name='dispatch')
class InternalGuestPasswd(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        return JsonResponse({
            'passwd': RotatingCode.get(),
            'expire': int(RotatingCode.remaining_time())
        })


@method_decorator(staff_member_required, name='dispatch')
class InternalBulkUserUpload(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        form = UserBulkImportForm(request.POST, request.FILES)
        if not form.is_valid():
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            })

        return JsonResponse({
            'status': 'ok',
            'count': form.validate_data(write=True),
        })

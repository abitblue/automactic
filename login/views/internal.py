from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from login.forms import UserBulkImportForm


@method_decorator(staff_member_required, name='dispatch')
class InternalBulkUserUpload(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        form = UserBulkImportForm(request.POST, request.FILES)
        if not form.is_valid():
            return JsonResponse({
                'status': 'error',
                'errors': [errors for field, errors in form.errors.items()]
            })

        return JsonResponse({
            'status': 'ok',
            'count': form.write_data(validated=True),
        })
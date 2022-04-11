import logging
from django.http import HttpRequest
from django.shortcuts import render
from django.views import View

from login.forms import IndexAuthenticationForm


logger = logging.getLogger('views.teachers')

class Teachers(View):
    template_name = 'teachers.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.template_name, {'form': IndexAuthenticationForm()})


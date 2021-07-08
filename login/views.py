from django.http import HttpRequest
from django.shortcuts import render
from django.views import View


class Index(View):
    template_name = 'index.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.template_name)

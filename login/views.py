from django.http import HttpRequest
from django.shortcuts import render
from django.views import View


class Index(View):
    template_name = 'index.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.template_name)

    # TODO: Rate limit post requests to index


class Error(View):
    template_name = 'index.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.template_name)


class Success(View):
    template_name = 'index.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.template_name)

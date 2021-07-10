from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from .forms import IndexAuthenticationForm
from .models import User, LoginHistory


class Index(View):
    template_name = 'index.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        print(dict(request.session))
        return render(request, self.template_name, {'form': IndexAuthenticationForm()})

    def post(self, request: HttpRequest, *args, **kwargs):
        form = IndexAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            print(form.cleaned_data)
        else:
            LoginHistory.log(user=form.cleaned_data.get('username'), logged_in=form.password_correct)
            return render(request, self.template_name, {'form': form})
        return HttpResponseRedirect('/')


class Error(View):
    template_name = 'index.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.template_name)


class Success(View):
    template_name = 'index.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.template_name)

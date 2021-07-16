from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from netaddr import IPNetwork

from .forms import IndexAuthenticationForm, DeviceForm
from .models import User, LoginHistory
from .utils import attach_mac_to_session, restrict_to


@method_decorator(restrict_to(IPNetwork('192.0.2.0/23')), name='dispatch')
class Index(View):
    template_name = 'login_page.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        print(dict(request.session))
        return render(request, self.template_name, {'form': IndexAuthenticationForm()})

    @method_decorator(attach_mac_to_session)
    def post(self, request: HttpRequest, *args, **kwargs):
        form = IndexAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            print(form.cleaned_data)
        else:
            LoginHistory.log(user=form.cleaned_data.get('username'), logged_in=form.password_correct)
            return render(request, self.template_name, {'form': form})
        return HttpResponseRedirect('/')


class Homepage(View):
    template_name = 'index.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        print("JKSLDJASA")
        return render(request, self.template_name, {'form': DeviceForm()})

    def post(self, request: HttpRequest, *args, **kwargs):
        form = DeviceForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
        else:
            return render(request, self.template_name, {'form': form})

        os = form.cleaned_data['device_os']
        return redirect(reverse('instructions') + f'?os={os}')


class Error(View):
    template_name = 'index.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        print("JKSLDJASA")
        return render(request, self.template_name)


class Success(View):
    template_name = 'index.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.template_name)


class InstructionsPage(View):
    template_name = 'instructions.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        device_os = request.GET.get('os', None)
        if device_os is None:
            return redirect('index')

        if device_os == 'mac':
            return redirect('login')

        return render(request, self.template_name, {
            'form': DeviceForm({
                'device_os': device_os
            }),
            'device_os': device_os,
        })

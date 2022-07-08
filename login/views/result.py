from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from enum import Enum, auto


class Success(View):
    template_name = 'login/success.html'

    def get(self, request: HttpRequest):
        return render(request, self.template_name)


class Error(View):
    template_name = 'login/error.html'

    # Map from Error to Verbose Name and Possible fixes
    err_map: dict[str, tuple[str, list[str]]] = {
        'unknown': (
            'Unknown Error',
            ['We were unable to process your request.',
             'Please seek assistance in room C56.']
        ),
        'alreadyRegistered': (
            'Your device is already registered',
            ['Ensure that MAC address randomization is turned off for the WiFi network, ncpsp.',
             'Connect to "ncpsp" with the password: 605D785001@rackID78R60']
        ),
        'unknownMAC': (
            'We could not determine your MAC address',
            ['Please seek assistance in room C56.']
        ),
        'wrongNetwork': (
            'You are connecting from the wrong network',
            ['Please connect using the JoinForWifi network and try again.']
        ),
        'clearpassAPI': (
            'Internal server error',
            ['Seek assistance in room C56 or send an email to <i>byod@sitechhs.com</i> with a screenshot of this page.']
        ),
    }

    def get(self, request: HttpRequest):
        err: str = request.GET.get('reason', 'unknown')
        verbose_message, fixes = self.err_map.get(err, self.err_map['unknown'])

        return render(request, self.template_name, {
            'error_message': verbose_message,
            'error_fixes': fixes
        })

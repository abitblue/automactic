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

    # Because the 'alreadyRegistered' reason is so prevalent, we move it to its own page to mirror the success page
    already_registered_template_name = 'login/error_already_registered.html'

    # Map from Error to Verbose Name and Possible fixes
    err_map: dict[str, tuple[str, list[str]]] = {
        'unknown': (
            'Unknown Error',
            ['We were unable to process your request.',
             'Please seek assistance in room C56.']
        ),
        'unknownMAC': (
            'We could not determine your MAC address',
            ['Please seek assistance in room C56.']
        ),
        'incorrectMAC': (
            'The MAC address you entered is not valid.',
            ['Please check the instructions and enter the correct MAC address.']
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
        err_msg: str = request.GET.get('err_msg', '')
        verbose_message, fixes = self.err_map.get(err, self.err_map['unknown'])

        template = self.template_name if err != 'alreadyRegistered' else self.already_registered_template_name

        return render(request, template, {
            'error_message': verbose_message,
            'error_fixes': fixes
        })

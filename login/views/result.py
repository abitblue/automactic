from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from enum import Enum, auto


class Success(View):
    template_name = 'login/success.html'

    def get(self, request: HttpRequest):
        return render(request, self.template_name)


class ErrorType(Enum):
    Unknown = auto()
    AlreadyRegistered = auto()
    UnknownMAC = auto()
    WrongNetwork = auto()
    ClearpassAPI = auto()


class Error(View):
    template_name = 'login/error.html'

    # Map from Error to Verbose Name and Possible fixes
    err_map: dict[ErrorType, tuple[str, list[str]]] = {
        ErrorType.Unknown: (
            'Unknown Error',
            ['We were unable to process your request',
             'Please seek assistance in room C56']
        ),
        ErrorType.AlreadyRegistered: (
            'Your device is already registered',
            ['Ensure that MAC address randomization is turned off for the WiFi network, ncpsp.',
             'Connect to "ncpsp" with the password: 605D785001@rackID78R60']
        ),
        ErrorType.UnknownMAC: (
            'We could not determine your MAC address',
            ['Please seek assistance in room C56.']
        ),
        ErrorType.WrongNetwork: (
            'You are connecting from the wrong network',
            ['Please connect using the JoinForWifi network.']
        ),
        ErrorType.ClearpassAPI: (
            'Internal server error',
            [
                'Seek assistance in room C-56, or send an email to <i>byod@sitechhs.com</i> with a screenshot of this page.']
        ),
    }

    def get(self, request: HttpRequest):
        request.session['error'] = ErrorType.AlreadyRegistered

        err: ErrorType = request.session.get('error', ErrorType.Unknown)
        verbose_message, fixes = self.err_map[err]

        return render(request, self.template_name, {
            'error_message': verbose_message,
            'error_fixes': fixes
        })

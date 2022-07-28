from django.shortcuts import render
from django.views import View
from django.http import HttpRequest


class Login(View):
    def get(self, request: HttpRequest, usertype: str):
        return render(request, f'login/{usertype}.html')

from django.shortcuts import render
from django.views import View
from django.http import HttpRequest


class Students(View):
    template_name = "login/students.html"

    def get(self, request: HttpRequest):
        return render(request, self.template_name)


class Teachers(View):
    template_name = "login/teachers.html"

    def get(self, request: HttpRequest):
        return render(request, self.template_name)


from django.shortcuts import render
from django.views import View
from django.http import HttpRequest


class Login(View):
    def get(self, request: HttpRequest, usertype: str, *args, **kwargs):
        kiosk: bool = kwargs.pop('kiosk', False)
        base_dir: str = 'login/batch' if not kiosk else 'login/kiosk'

        help_template = {
            'student': f"{base_dir}/students.html",
            'teacher': f"{base_dir}/teachers.html"
        }

        return render(request, f'login/login.html', {
            'usertype': usertype.capitalize(),
            'help_template': help_template[usertype]
        })

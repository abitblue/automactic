import random

from django.http import HttpRequest
from django.shortcuts import render
from django.views import View


class Success(View):
    template_name = 'error.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.template_name)


class Error(View):
    template_name = 'error.html'
    
    lines = [
        "Something didn't go as planned.",
        "Maybe you broke something?",
        "You done did it again...",
        "Quick Ma! Call the administration!",
        "Look ma, no hands!",
        "Task failed successfully.",
        "It seems like you haven't gotten an error in a while.",
        "Something bad.",
        "Run away as fast as you can.",
        "Catastrophic failure.",
        "PEBCAK",
        "Biological Interface Error.",
        "Everything is fine. Trust me.",
        "Oops!",
        "This is a good time to display an error.",
        "Why did you do that?",
        "I would blame the sysadmins.",
        "Well this is awkward...",
        "That hurt.",
        "Oof!",
        "Here's some cake to make you feel better. 🎂"
    ]

    def get(self, request: HttpRequest, *args, **kwargs):
        msg = request.GET.get('error', None)
        return render(request, self.template_name, {
            'witty_line': random.choice(self.lines),
            'error_message': msg if msg is not None else 'Unknown error',
        })

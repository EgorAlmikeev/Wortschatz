from django.shortcuts import render
from django.http import HttpRequest
from django.contrib.auth.models import User


def home(request: HttpRequest):
    return render(request, 'home.html')

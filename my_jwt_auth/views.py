from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.forms import UserCreationForm


def login(request: HttpRequest):
    return render(request, 'login.html')

def register(request: HttpRequest):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid:
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, "register.html", {"form": form})
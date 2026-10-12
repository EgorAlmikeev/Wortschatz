from django.shortcuts import render
from django.http import HttpRequest
from django.contrib.auth.models import User


def home(request: HttpRequest):
    return render(request, 'home.html')


def collections(request: HttpRequest):
    return render(request, 'collections.html')


def collection_detail(request: HttpRequest, collection_id: int):
    return render(request, 'collection_detail.html', {'collection_id': collection_id})


def profile(request: HttpRequest):
    return render(request, 'profile.html')

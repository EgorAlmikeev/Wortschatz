from django.shortcuts import render
from django.http import HttpRequest
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer

def login(request: HttpRequest):
    return render(request, 'login.html')

def register(request: HttpRequest):
    return render(request, "register.html")


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

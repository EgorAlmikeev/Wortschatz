"""
URL configuration for wortschatz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

import word_collection.views
import word_collection.urls
import my_jwt_auth.views
import my_jwt_auth.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(word_collection.urls)),
    path('api/auth/', include(my_jwt_auth.urls)),
    path('api/auth/', include(my_jwt_auth.urls)),
    path('login/', my_jwt_auth.views.login, name='login_page'),
    path('register/', my_jwt_auth.views.register, name='register_page'),
    path('my_words/', word_collection.views.my_words, name='my_words')
]

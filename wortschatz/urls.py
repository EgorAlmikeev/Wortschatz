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
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

import word_collection.views
import word_collection.urls
import my_jwt_auth.views
import my_jwt_auth.urls
from .views import home

urlpatterns = [
    # Home page
    path('', home, name = 'home'),
    # Admin page
    path('admin/', admin.site.urls),
    # OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redoc UI
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # JWT API
    path('auth/', include(my_jwt_auth.urls)),
    # JWT login page
    path('login/', my_jwt_auth.views.login, name='login_page'),
    # JWT registration page
    path('register/', my_jwt_auth.views.register, name='register_page'),
    # Word collection page
    path('my_words/', word_collection.views.my_words, name='my_words'),
    # Word collection API
    path('api/', include(word_collection.urls)),
]

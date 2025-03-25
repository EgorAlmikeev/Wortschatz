from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import WordViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'words', WordViewSet, basename='word')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.http import HttpRequest

from .models import Word, Category
from .serializers import WordSerializer, CategorySerializer

class WordPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class WordViewSet(viewsets.ModelViewSet):
    serializer_class = WordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = WordPagination

    def get_queryset(self):
        return Word.objects.filter(owner = self.request.user).order_by("-created_date_time")
    
    def perform_create(self, serializer):
        return serializer.save(owner = self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(owner = self.request.user)
    
    def perform_create(self, serializer):
        return serializer.save(owner = self.request.user)

def my_words(request: HttpRequest):
    return render(request, 'my_words.html')
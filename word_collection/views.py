from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Word, Category
from .serializers import WordSerializer, CategorySerializer
from .utils import get_superuser_id

class WordViewSet(viewsets.ModelViewSet):
    serializer_class = WordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Word.objects.filter(owner = self.request.user)
    
    def perform_create(self, serializer):
        return serializer.save(owner = self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(Q(owner = self.request.user) | Q(owner = get_superuser_id))
    
    def perform_create(self, serializer):
        return serializer.save(owner = self.request.user)

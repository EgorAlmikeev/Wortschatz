from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.http import HttpRequest
from django_filters.rest_framework import DjangoFilterBackend

from .models import Word, Category
from .serializers import (
    CategorySerializer,
    WordDetailSerializer,
    WordListSerializer,
)
from .permissions import IsOwnerOrReadOnly
from .filters import WordFilter


class WordPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class WordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = WordPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = WordFilter

    def get_queryset(self):
        qs = Word.objects.filter(owner=self.request.user).order_by("-created_date_time")
        if self.action == "retrieve":
            qs = qs.select_related("owner").prefetch_related(
                "translations",
                "examples",
                "forms",
                "prepositions_and_cases_with_translations",
            )
        else:
            qs = qs.select_related("owner")
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return WordListSerializer
        return WordDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Category.objects.select_related("owner").filter(owner=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)


def my_words(request: HttpRequest):
    return render(request, "my_words.html")

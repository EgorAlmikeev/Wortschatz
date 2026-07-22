from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from django.http import HttpRequest
from django_filters.rest_framework import DjangoFilterBackend

from .models import Collection, Tag, Word
from .serializers import (
    CollectionSerializer,
    TagSerializer,
    WordDetailSerializer,
    WordListSerializer,
    WordFormSerializer,
    WordExampleSerializer,
    WordTranslationSerializer,
    WordPrepositionAndCaseWithTranslationSerializer,
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

    @action(detail=True, methods=["post"])
    def add_word_form(self, request, pk=None):
        word = self.get_object()
        form_data = request.data
        serializer = WordFormSerializer(data=form_data)
        serializer.is_valid(raise_exception=True)
        word.forms.create(**serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"])
    def remove_word_form(self, request, pk=None):
        word = self.get_object()
        form_id = request.data.get("form_id")
        form = get_object_or_404(word.forms, id=form_id)
        form.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=["post"])
    def add_word_example(self, request, pk=None):
        word = self.get_object()
        example_data = request.data
        serializer = WordExampleSerializer(data=example_data)
        serializer.is_valid(raise_exception=True)
        word.examples.create(**serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"])
    def remove_word_example(self, request, pk=None):
        word = self.get_object()
        example_id = request.data.get("example_id")
        example = get_object_or_404(word.examples, id=example_id)
        example.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def add_word_translation(self, request, pk=None):
        word = self.get_object()
        translation_data = request.data
        serializer = WordTranslationSerializer(data=translation_data)
        serializer.is_valid(raise_exception=True)
        word.translations.create(**serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["delete"])
    def remove_word_translation(self, request, pk=None):
        word = self.get_object()
        translation_id = request.data.get("translation_id")
        translation = get_object_or_404(word.translations, id=translation_id)
        translation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Tag.objects.select_related("owner").filter(owner=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Collection.objects.select_related("owner").prefetch_related(
            "words", "tags"
        ).filter(owner=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=["post"])
    def add_word(self, request, pk=None):
        collection = self.get_object()
        word = get_object_or_404(
            Word,
            pk=request.data["word_id"],
            owner=request.user,
        )

        collection.words.add(word)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=["delete"])
    def remove_word(self, request, pk=None):
        collection = self.get_object()
        word = get_object_or_404(
            Word,
            pk=request.data["word_id"],
            owner=request.user,
        )

        collection.words.remove(word)

        return Response(status=status.HTTP_204_NO_CONTENT)

def my_words(request: HttpRequest):
    return render(request, "my_words.html")

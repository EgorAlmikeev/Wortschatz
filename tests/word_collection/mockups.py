from django.contrib.auth.models import User

from word_collection.serializers import CategorySerializer, WordDetailSerializer
from tests.word_collection.factories import (
    CategoryFactory,
    WordFactory,
    WordPayloadFactory,
    CategoryPayloadFactory,
)


class Mockups:
    @staticmethod
    def generate_word_payload(owner: User):
        return WordPayloadFactory()

    @staticmethod
    def generate_category_payload(owner: User):
        return CategoryPayloadFactory()

    @staticmethod
    def create_word(owner: User):
        model = WordFactory.create(owner=owner)
        json = WordDetailSerializer(model).data
        return model, json

    @staticmethod
    def create_category(owner: User):
        model = CategoryFactory.create(owner=owner)
        json = CategorySerializer(model).data
        return model, json

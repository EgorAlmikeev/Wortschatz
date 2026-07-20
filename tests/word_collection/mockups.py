from django.contrib.auth.models import User

from word_collection.serializers import TagSerializer, WordDetailSerializer
from tests.word_collection.factories import (
    TagFactory,
    TagPayloadFactory,
    WordFactory,
    WordPayloadFactory,
)


class Mockups:
    @staticmethod
    def generate_word_payload(owner: User):
        return WordPayloadFactory()

    @staticmethod
    def generate_tag_payload(owner: User):
        return TagPayloadFactory()

    @staticmethod
    def create_word(owner: User):
        model = WordFactory.create(owner=owner)
        json = WordDetailSerializer(model).data
        return model, json

    @staticmethod
    def create_tag(owner: User):
        model = TagFactory.create(owner=owner)
        json = TagSerializer(model).data
        return model, json

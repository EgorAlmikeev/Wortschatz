from django.contrib.auth.models import User

from word_collection.serializers import CollectionSerializer, TagSerializer, WordDetailSerializer
from tests.word_collection.factories import (
    CollectionFactory,
    CollectionPayloadFactory,
    TagFactory,
    TagPayloadFactory,
    WordFactory,
    WordPayloadFactory,
)

class Mockups:
    """
    Words
    """
    @staticmethod
    def generate_word_payload():
        return WordPayloadFactory()

    @staticmethod
    def create_word(owner: User):
        model = WordFactory.create(owner=owner)
        json = WordDetailSerializer(model).data
        return model, json
    
    """
    Tags
    """
    @staticmethod
    def generate_tag_payload():
        return TagPayloadFactory()
    
    @staticmethod
    def create_tag(owner: User):
        model = TagFactory.create(owner=owner)
        json = TagSerializer(model).data
        return model, json

    """
    Collections
    """
    @staticmethod
    def generate_collection_payload():
        return CollectionPayloadFactory()

    @staticmethod
    def create_collection(owner: User):
        model = CollectionFactory.create(owner=owner)
        json = CollectionSerializer(model).data
        return model, json

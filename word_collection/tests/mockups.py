from django.contrib.auth.models import User

from word_collection.serializers import CategorySerializer, WordSerializer
from word_collection.tests.factories import CategoryFactory, WordFactory

class Mockups:
    @staticmethod
    def build_word(owner: User):
        model = WordFactory.build(owner=owner)
        json = WordSerializer(model).data
        return model, json
    
    @staticmethod
    def build_category(owner: User):
        model = CategoryFactory.build(owner=owner)
        json = CategorySerializer(model).data
        return model, json
    
    @staticmethod
    def create_word(owner: User):
        model = WordFactory.create(owner=owner)
        json = WordSerializer(model).data
        return model, json
    
    @staticmethod
    def create_category(owner: User):
        model = CategoryFactory.create(owner=owner)
        json = CategorySerializer(model).data
        return model, json
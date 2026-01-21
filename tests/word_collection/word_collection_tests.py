import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from tests.word_collection.mockups import Mockups as WordCollectionMocups
from my_jwt_auth.mockups import Mockups as JWTMockups

class TestWordCollection:

    def setup_method(self, method):
        print()
        print(f"=== creating user for a '{method.__name__}' test ===")
        self.user = User.objects.create_user(username=JWTMockups.user['username'], password=JWTMockups.user['password'])
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @pytest.mark.django_db
    def test_create_word(self):
        _, word_json = WordCollectionMocups.build_word(self.user)
        response = self.client.post('/api/words/', word_json, format='json')

        assert response.status_code == 201
        assert response.data['definition'] == word_json['definition']
        assert response.data['translations'] == word_json['translations']
        assert response.data['examples'] == word_json['examples']
        assert response.data['other_forms'] == word_json['other_forms']
        assert response.data['part_of_speech_id'] == word_json['part_of_speech_id']
        assert response.data['genus_id'] == word_json['genus_id']
    
    @pytest.mark.django_db
    def test_create_category(self):
        _, category_json = WordCollectionMocups.build_category(self.user)
        response = self.client.post('/api/categories/', category_json, format='json')
        
        assert response.status_code == 201
        assert response.data['name'] == category_json['name']

    @pytest.mark.django_db
    def test_create_word_with_category(self):
        category, _ = WordCollectionMocups.create_category(self.user)
        _, word_json = WordCollectionMocups.build_word(self.user)
        word_json['categories'] = [category.id]
        response = self.client.post('/api/words/', word_json, format='json')

        assert response.status_code == 201
        assert response.data['categories'] == [category.id]

    @pytest.mark.django_db
    def test_update_word(self):
        word, word_json = WordCollectionMocups.create_word(self.user)
        word_json['definition'] = 'updated definition'
        response = self.client.put(f'/api/words/{word.id}/', word_json, format='json')

        assert response.status_code == 200
        assert response.data['definition'] == word_json['definition']
    
    @pytest.mark.django_db
    def test_update_category(self):
        category, category_json = WordCollectionMocups.create_category(self.user)
        category_json['name'] = 'updated name'
        response = self.client.put(f'/api/categories/{category.id}/', category_json, format='json')

        assert response.status_code == 200
        assert response.data['name'] == category_json['name']
    
    @pytest.mark.django_db
    def test_delete_word(self):
        word, _ = WordCollectionMocups.create_word(self.user)
        response = self.client.delete(f'/api/words/{word.id}/')
        assert response.status_code == 204

        response = self.client.get(f'/api/words/{word.id}/')
        assert response.status_code == 404
    
    @pytest.mark.django_db
    def test_delete_category(self):
        category, _ = WordCollectionMocups.create_category(self.user)
        response = self.client.delete(f'/api/categories/{category.id}/')
        assert response.status_code == 204

        response = self.client.get(f'/api/categories/{category.id}/')
        assert response.status_code == 404

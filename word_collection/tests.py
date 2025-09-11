import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from word_collection.mockups import Mockups as WordCollectionMocups
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
        data = WordCollectionMocups.word_mockup.copy()
        response = self.client.post('/api/words/', data, format='json')

        assert response.status_code == 201
        assert response.data['definition'] == data['definition']
        assert response.data['translations'] == data['translations']
        assert response.data['examples'] == data['examples']
        assert response.data['other_forms'] == data['other_forms']
        assert response.data['part_of_speech_id'] == data['part_of_speech_id']
        assert response.data['genus_id'] == data['genus_id']
    
    @pytest.mark.django_db
    def test_create_category(self):
        data = WordCollectionMocups.category_mockup.copy()
        response = self.client.post('/api/categories/', data, format='json')
        
        assert response.status_code == 201
        assert response.data['name'] == data['name']

    @pytest.mark.django_db
    def test_create_word_with_category(self):
        category_data = WordCollectionMocups.category_mockup.copy()
        response = self.client.post('/api/categories/', category_data, format='json')
        
        assert response.status_code == 201
        assert response.data['name'] == category_data['name']

        word_data = WordCollectionMocups.word_mockup.copy()
        word_data['categories'] = [1]
        response = self.client.post('/api/words/', word_data, format='json')

        assert response.status_code == 201
        assert response.data['categories'] == [1]

    @pytest.mark.django_db
    def test_update_word(self):
        data = WordCollectionMocups.word_mockup.copy()
        response = self.client.post('/api/words/', data, format='json')
        
        if response.status_code != 201:
            print(response.data)

        assert response.status_code == 201
        assert response.data['definition'] == data['definition']

        data['definition'] = 'updated test definition'
        response = self.client.put('/api/words/1/', data, format='json')

        assert response.status_code == 200
        assert response.data['definition'] == data['definition']
    
    @pytest.mark.django_db
    def test_update_category(self):
        data = WordCollectionMocups.category_mockup.copy()
        response = self.client.post('/api/categories/', data, format='json')
        
        assert response.status_code == 201
        assert response.data['name'] == data['name']

        data['name'] = 'updated category name'
        response = self.client.put('/api/categories/1/', data, format='json')

        assert response.status_code == 200
        assert response.data['name'] == data['name']
    
    @pytest.mark.django_db
    def test_delete_word(self):
        data = WordCollectionMocups.word_mockup.copy()
        response = self.client.post('/api/words/', data, format='json')
        
        assert response.status_code == 201
        assert response.data['definition'] == data['definition']

        response = self.client.delete('/api/words/1/')
        assert response.status_code == 204

        response = self.client.get('/api/words/1/')
        assert response.status_code == 404
    
    @pytest.mark.django_db
    def test_delete_category(self):
        data = WordCollectionMocups.category_mockup.copy()
        response = self.client.post('/api/categories/', data, format='json')

        assert response.status_code == 201
        assert response.data['name'] == data['name']

        response = self.client.delete('/api/categories/1/')
        assert response.status_code == 204

        response = self.client.get('/api/categories/1/')
        assert response.status_code == 404

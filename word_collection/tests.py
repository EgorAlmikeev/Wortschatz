import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from word_collection.models import Word, Category
from word_collection.mockups import Mockups

class TestWordCollection:

    def setup_method(self, method):
        print()
        print(f"=== creating user for a '{method.__name__}' test ===")
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @pytest.mark.django_db
    def test_create_word(self):
        data = Mockups.word_mockup
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
        data = Mockups.category_mockup

        response = self.client.post('/api/categories/', data, format='json')

        if response.status_code != 201:
            print(response.data)
        
        assert response.status_code == 201
        assert response.data['name'] == data['name']

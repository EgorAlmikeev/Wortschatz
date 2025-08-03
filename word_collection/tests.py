import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from word_collection.models import Word, Category

@pytest.mark.django_db
def test_create_word():
    user = User.objects.create_user(username='testuser', password='12345')
    client = APIClient()
    client.force_authenticate(user=user)

    data = {
        'definition': 'test definition',
        'translations': ['test translation'],
        'examples': ['test example'],
        'other_forms': ['test other form'],
        'part_of_speech_id': 1,
        'genus_id': 1
    }

    response = client.post('/api/words/', data, format='json')

    if response.status_code != 201:
        print(response.data)

    assert response.status_code == 201
    assert response.data['definition'] == data['definition']
    assert response.data['translations'] == data['translations']
    assert response.data['examples'] == data['examples']
    assert response.data['other_forms'] == data['other_forms']
    assert response.data['part_of_speech_id'] == data['part_of_speech_id']
    assert response.data['genus_id'] == data['genus_id']

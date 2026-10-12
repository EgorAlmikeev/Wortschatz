import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from my_jwt_auth.mockups import Mockups as JWTMockups
from tests.word_collection.mockups import Mockups as WordCollectionMocups
from word_collection.models import Collection, Word

class TestJWTAuth:
    def setup_method(self, method):
        print()
        print(f"=== creating user for a '{method.__name__}' test ===")
        self.user = User.objects.create_user(username=JWTMockups.user['username'], password=JWTMockups.user['password'])
        self.client = APIClient()
    
    @pytest.mark.django_db
    def test_authenticate_user(self):
        data = JWTMockups.user

        response = self.client.post('/api/auth/token/', data, format='json')

        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    @pytest.mark.django_db
    def test_refresh_token(self):
        data = JWTMockups.user
        response = self.client.post('/api/auth/token/', data, format='json')
        refresh_token = response.data['refresh']

        response = self.client.post('/api/auth/token/refresh/', {'refresh': refresh_token}, format='json')

        assert response.status_code == 200
        assert 'access' in response.data
    
    @pytest.mark.django_db
    def test_verify_token(self):
        data = JWTMockups.user
        response = self.client.post('/api/auth/token/', data, format='json')
        access_token = response.data['access']

        response = self.client.post('/api/auth/token/verify/', {'token': access_token}, format='json')

        assert response.status_code == 200


class TestRegistration:
    def setup_method(self, method):
        print()
        print(f"=== preparing client for a '{method.__name__}' test ===")
        self.client = APIClient()

    @pytest.mark.django_db
    def test_register_user(self):
        data = {'username': 'new_user', 'password': 'a-strong-passw0rd'}

        response = self.client.post('/api/auth/register/', data, format='json')

        assert response.status_code == 201
        assert response.data['username'] == data['username']
        assert 'password' not in response.data

        user = User.objects.get(username=data['username'])
        assert user.check_password(data['password'])
        assert user.is_staff is False
        assert user.is_superuser is False

    @pytest.mark.django_db
    def test_register_user_duplicate_username(self):
        data = {'username': JWTMockups.user['username'], 'password': 'a-strong-passw0rd'}
        User.objects.create_user(username=data['username'], password='irrelevant')

        response = self.client.post('/api/auth/register/', data, format='json')

        assert response.status_code == 400

    @pytest.mark.django_db
    def test_register_user_weak_password(self):
        data = {'username': 'new_user', 'password': '12345'}

        response = self.client.post('/api/auth/register/', data, format='json')

        assert response.status_code == 400
        assert not User.objects.filter(username=data['username']).exists()

    @pytest.mark.django_db
    def test_register_user_cannot_set_admin_flags(self):
        data = {
            'username': 'new_user',
            'password': 'a-strong-passw0rd',
            'is_staff': True,
            'is_superuser': True,
        }

        response = self.client.post('/api/auth/register/', data, format='json')

        assert response.status_code == 201
        user = User.objects.get(username=data['username'])
        assert user.is_staff is False
        assert user.is_superuser is False

    @pytest.mark.django_db
    def test_register_user_creates_default_collection(self):
        data = {'username': 'new_user', 'password': 'a-strong-passw0rd'}

        self.client.post('/api/auth/register/', data, format='json')
        user = User.objects.get(username=data['username'])

        assert Collection.objects.filter(owner=user).count() == 1
        assert Word.objects.filter(owner=user).count() == 5

        collection = Collection.objects.get(owner=user)
        assert collection.name
        assert collection.description
        assert collection.image_url
        assert collection.background_color
        assert collection.words.count() == 5
        assert collection.tags.count() >= 1

        for word in Word.objects.filter(owner=user):
            assert word.definition
            assert word.genus_id is not None
            assert word.part_of_speech_id is not None
            assert word.image_url
            assert word.translations.exists()
            assert word.examples.exists()
            assert word.forms.exists()
            assert word.prepositions_and_cases_with_translations.exists()


class TestProfile:
    def setup_method(self, method):
        print()
        print(f"=== creating user for a '{method.__name__}' test ===")
        self.user = User.objects.create_user(username=JWTMockups.user['username'], password=JWTMockups.user['password'])
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @pytest.mark.django_db
    def test_get_profile_requires_auth(self):
        client = APIClient()

        response = client.get('/api/auth/me/')

        assert response.status_code == 401

    @pytest.mark.django_db
    def test_get_profile(self):
        response = self.client.get('/api/auth/me/')

        assert response.status_code == 200
        assert response.data['username'] == self.user.username
        assert 'date_joined' in response.data
        assert 'password' not in response.data

    @pytest.mark.django_db
    def test_change_password(self):
        data = {'old_password': JWTMockups.user['password'], 'new_password': 'a-strong-passw0rd'}

        response = self.client.post('/api/auth/change-password/', data, format='json')

        assert response.status_code == 204
        self.user.refresh_from_db()
        assert self.user.check_password('a-strong-passw0rd')

    @pytest.mark.django_db
    def test_change_password_wrong_old_password(self):
        data = {'old_password': 'not-the-right-password', 'new_password': 'a-strong-passw0rd'}

        response = self.client.post('/api/auth/change-password/', data, format='json')

        assert response.status_code == 400
        self.user.refresh_from_db()
        assert self.user.check_password(JWTMockups.user['password'])

    @pytest.mark.django_db
    def test_change_password_weak_new_password(self):
        data = {'old_password': JWTMockups.user['password'], 'new_password': '12345'}

        response = self.client.post('/api/auth/change-password/', data, format='json')

        assert response.status_code == 400
        self.user.refresh_from_db()
        assert self.user.check_password(JWTMockups.user['password'])

    @pytest.mark.django_db
    def test_delete_account(self):
        WordCollectionMocups.create_word(self.user)
        WordCollectionMocups.create_collection(self.user)

        response = self.client.delete('/api/auth/me/')

        assert response.status_code == 204
        assert not User.objects.filter(id=self.user.id).exists()
        assert not Word.objects.filter(owner_id=self.user.id).exists()
        assert not Collection.objects.filter(owner_id=self.user.id).exists()

    @pytest.mark.django_db
    def test_delete_account_requires_auth(self):
        client = APIClient()

        response = client.delete('/api/auth/me/')

        assert response.status_code == 401
        assert User.objects.filter(id=self.user.id).exists()

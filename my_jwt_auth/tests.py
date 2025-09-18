import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from my_jwt_auth.mockups import Mockups as JWTMockups

class TestJWTAuth:
    def setup_method(self, method):
        print()
        print(f"=== creating user for a '{method.__name__}' test ===")
        self.user = User.objects.create_user(username=JWTMockups.user['username'], password=JWTMockups.user['password'])
        self.client = APIClient()
    
    @pytest.mark.django_db
    def test_authenticate_user(self):
        data = JWTMockups.user

        response = self.client.post('/auth/token/', data, format='json')

        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    @pytest.mark.django_db
    def test_refresh_token(self):
        data = JWTMockups.user
        response = self.client.post('/auth/token/', data, format='json')
        refresh_token = response.data['refresh']

        response = self.client.post('/auth/token/refresh/', {'refresh': refresh_token}, format='json')

        assert response.status_code == 200
        assert 'access' in response.data
    
    @pytest.mark.django_db
    def test_verify_token(self):
        data = JWTMockups.user
        response = self.client.post('/auth/token/', data, format='json')
        access_token = response.data['access']

        response = self.client.post('/auth/token/verify/', {'token': access_token}, format='json')

        assert response.status_code == 200
        
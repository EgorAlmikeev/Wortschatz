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

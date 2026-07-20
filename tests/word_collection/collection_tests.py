import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from tests.word_collection.mockups import Mockups as WordCollectionMocups
from my_jwt_auth.mockups import Mockups as JWTMockups


class TestCollectionModel:

    def setup_method(self, method):
        print()
        print(f"=== creating user for a '{method.__name__}' test ===")
        self.user = User.objects.create_user(
            username=JWTMockups.user["username"], password=JWTMockups.user["password"]
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @pytest.mark.django_db
    def test_create_collection(self):
        collection_json = WordCollectionMocups.generate_collection_payload()
        response = self.client.post("/api/collections/", collection_json, format="json")

        assert response.status_code == 201
        assert response.data["name"] == collection_json["name"]
        assert response.data["description"] == collection_json["description"]

    @pytest.mark.django_db
    def test_update_collection(self):
        collection, collection_json = WordCollectionMocups.create_collection(self.user)
        collection_json["name"] = "updated name"
        collection_json["description"] = "updated description"
        response = self.client.put(
            f"/api/collections/{collection.id}/", collection_json, format="json"
        )

        assert response.status_code == 200
        assert response.data["name"] == collection_json["name"]
        assert response.data["description"] == collection_json["description"]

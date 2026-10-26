import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from tests.word_collection.mockups import Mockups as WordCollectionMocups
from tests.word_collection.factories import TagFactory
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

    @pytest.mark.django_db
    def test_delete_collection(self):
        collection, _ = WordCollectionMocups.create_collection(self.user)
        response = self.client.delete(f"/api/collections/{collection.id}/")
        assert response.status_code == 204

        response = self.client.get(f"/api/collections/{collection.id}/")
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_collection_add_word(self):
        collection, _ = WordCollectionMocups.create_collection(self.user)
        word, _ = WordCollectionMocups.create_word(self.user)

        assert word.id not in [w["id"] for w in collection.words.all().values("id")]

        response = self.client.post(f"/api/collections/{collection.id}/add_word/", {"word_id": word.id}, format="json")
        assert response.status_code == 204

        response = self.client.get(f"/api/collections/{collection.id}/")
        assert response.status_code == 200
        assert any(word_id == word.id for word_id in response.data["words"])

        response = self.client.get(f"/api/words/{word.id}/")
        assert response.status_code == 200
        assert any(collection_id == collection.id for collection_id in response.data["collections"])

    @pytest.mark.django_db
    def test_collection_remove_word(self):
        collection, _ = WordCollectionMocups.create_collection(self.user)
        word, _ = WordCollectionMocups.create_word(self.user)

        collection.words.add(word)
        assert any(word_id == word.id for word_id in collection.words.values_list("id", flat=True))

        response = self.client.delete(f"/api/collections/{collection.id}/remove_word/", {"word_id": word.id}, format="json")
        assert response.status_code == 204

        response = self.client.get(f"/api/collections/{collection.id}/")
        assert response.status_code == 200
        assert all(word_id != word.id for word_id in response.data["words"])

        response = self.client.get(f"/api/words/{word.id}/")
        assert response.status_code == 200
        assert all(collection_id != collection.id for collection_id in response.data["collections"])

    @pytest.mark.django_db
    def test_collection_add_tag(self):
        collection, _ = WordCollectionMocups.create_collection(self.user)
        tag = TagFactory.create(owner=self.user)

        assert all(t.id != tag.id for t in collection.tags.all())

        response = self.client.post(
            f"/api/collections/{collection.id}/add_tag/", {"tag_id": tag.id}, format="json"
        )
        assert response.status_code == 204

        response = self.client.get(f"/api/collections/{collection.id}/")
        assert response.status_code == 200
        assert any(t["id"] == tag.id for t in response.data["tags"])

    @pytest.mark.django_db
    def test_collection_remove_tag(self):
        collection, _ = WordCollectionMocups.create_collection(self.user)
        tag = TagFactory.create(owner=self.user)

        collection.tags.add(tag)
        assert any(t.id == tag.id for t in collection.tags.all())

        response = self.client.delete(
            f"/api/collections/{collection.id}/remove_tag/", {"tag_id": tag.id}, format="json"
        )
        assert response.status_code == 204

        response = self.client.get(f"/api/collections/{collection.id}/")
        assert response.status_code == 200
        assert all(t["id"] != tag.id for t in response.data["tags"])

    @pytest.mark.django_db
    def test_filter_collections_by_tag_id(self):
        tag_a = TagFactory.create(owner=self.user)
        tag_b = TagFactory.create(owner=self.user)
        collection_a, _ = WordCollectionMocups.create_collection(self.user)
        collection_b, _ = WordCollectionMocups.create_collection(self.user)
        collection_c, _ = WordCollectionMocups.create_collection(self.user)
        collection_a.tags.add(tag_a)
        collection_b.tags.add(tag_b)

        response = self.client.get(f"/api/collections/?tag_id={tag_a.id}")
        assert response.status_code == 200
        returned_ids = {c["id"] for c in response.data}
        assert returned_ids == {collection_a.id}

        response = self.client.get(f"/api/collections/?tag_id={tag_a.id},{tag_b.id}")
        assert response.status_code == 200
        returned_ids = {c["id"] for c in response.data}
        assert returned_ids == {collection_a.id, collection_b.id}
        assert collection_c.id not in returned_ids
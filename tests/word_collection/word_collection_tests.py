import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from tests.word_collection.mockups import Mockups as WordCollectionMocups
from my_jwt_auth.mockups import Mockups as JWTMockups


class TestWordCollection:

    def setup_method(self, method):
        print()
        print(f"=== creating user for a '{method.__name__}' test ===")
        self.user = User.objects.create_user(
            username=JWTMockups.user["username"], password=JWTMockups.user["password"]
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @pytest.mark.django_db
    def test_create_word(self):
        word_json = WordCollectionMocups.generate_word_payload()
        response = self.client.post("/api/words/", word_json, format="json")

        assert response.status_code == 201
        assert response.data["definition"] == word_json["definition"]

        for translation in response.data["translations"]:
            assert translation["translation"] in [
                ex["translation"] for ex in word_json["translations"]
            ]

        for example in response.data["examples"]:
            assert example["sentence"] in [
                ex["sentence"] for ex in word_json["examples"]
            ]
            assert example["translation"] in [
                ex["translation"] for ex in word_json["examples"]
            ]

        for form in response.data["forms"]:
            assert form["form"] in [f["form"] for f in word_json["forms"]]

        assert response.data["part_of_speech_id"] == word_json["part_of_speech_id"]
        assert response.data["genus_id"] == word_json["genus_id"]

    @pytest.mark.django_db
    def test_create_tag(self):
        tag_json = WordCollectionMocups.generate_tag_payload()
        response = self.client.post("/api/tags/", tag_json, format="json")

        assert response.status_code == 201
        assert response.data["name"] == tag_json["name"]

    @pytest.mark.django_db
    def test_create_collection(self):
        collection_json = WordCollectionMocups.generate_collection_payload()
        response = self.client.post("/api/collections/", collection_json, format="json")

        assert response.status_code == 201
        assert response.data["name"] == collection_json["name"]
        assert response.data["description"] == collection_json["description"]

    @pytest.mark.django_db
    def test_update_word(self):
        word, word_json = WordCollectionMocups.create_word(self.user)
        word_json["definition"] = "updated definition"
        response = self.client.put(f"/api/words/{word.id}/", word_json, format="json")

        assert response.status_code == 200
        assert response.data["definition"] == word_json["definition"]

    @pytest.mark.django_db
    def test_partial_update_word(self):
        word, _ = WordCollectionMocups.create_word(self.user)
        patch_json = {
            "examples": [
                {"sentence": "updated sentence", "translation": "updated translation"}
            ]
        }
        response = self.client.patch(
            f"/api/words/{word.id}/", patch_json, format="json"
        )

        assert response.status_code == 200

        for example in response.data["examples"]:
            assert example["sentence"] in [
                ex["sentence"] for ex in patch_json["examples"]
            ]
            assert example["translation"] in [
                ex["translation"] for ex in patch_json["examples"]
            ]

        assert response.data["definition"] == word.definition

    @pytest.mark.django_db
    def test_update_tag(self):
        tag, tag_json = WordCollectionMocups.create_tag(self.user)
        tag_json["name"] = "updated name"
        response = self.client.put(
            f"/api/tags/{tag.id}/", tag_json, format="json"
        )

        assert response.status_code == 200
        assert response.data["name"] == tag_json["name"]

    @pytest.mark.django_db
    def test_delete_word(self):
        word, _ = WordCollectionMocups.create_word(self.user)
        response = self.client.delete(f"/api/words/{word.id}/")
        assert response.status_code == 204

        response = self.client.get(f"/api/words/{word.id}/")
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_delete_tag(self):
        tag, _ = WordCollectionMocups.create_tag(self.user)
        response = self.client.delete(f"/api/tags/{tag.id}/")
        assert response.status_code == 204

        response = self.client.get(f"/api/tags/{tag.id}/")
        assert response.status_code == 404

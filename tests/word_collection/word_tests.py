import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from tests.word_collection.mockups import Mockups as WordCollectionMocups
from my_jwt_auth.mockups import Mockups as JWTMockups

class TestWordModel:

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
    def test_update_word(self):
        word, word_json = WordCollectionMocups.create_word(self.user)
        word_json["definition"] = "updated definition"
        response = self.client.put(f"/api/words/{word.id}/", word_json, format="json")

        assert response.status_code == 200
        assert response.data["definition"] == word_json["definition"]

    @pytest.mark.django_db
    def test_delete_word(self):
        word, _ = WordCollectionMocups.create_word(self.user)
        response = self.client.delete(f"/api/words/{word.id}/")
        assert response.status_code == 204

        response = self.client.get(f"/api/words/{word.id}/")
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_add_word_form(self):
        word, _ = WordCollectionMocups.create_word(self.user)
        form_data = {"name": "test form name", "form": "test form value"}
        response = self.client.post(
            f"/api/words/{word.id}/add_word_form/", form_data, format="json"
        )

        assert response.status_code == 201
        assert response.data["name"] == form_data["name"]
        assert response.data["form"] == form_data["form"]

        assert any(
            form.name == form_data["name"] and form.form == form_data["form"]
            for form in word.forms.all()
        )

    @pytest.mark.django_db
    def test_remove_word_form(self):
        word, _ = WordCollectionMocups.create_word(self.user)
        assert word.forms.exists()

        form = word.forms.first()
        response = self.client.delete(
            f"/api/words/{word.id}/remove_word_form/", {"form_id": form.id}, format="json"
        )

        assert response.status_code == 204
        assert not word.forms.filter(id=form.id).exists()

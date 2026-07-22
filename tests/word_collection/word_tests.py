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
            f"/api/words/{word.id}/remove_word_form/", {"item_id": form.id}, format="json"
        )

        assert response.status_code == 204
        assert not word.forms.filter(id=form.id).exists()

    @pytest.mark.django_db
    def test_add_word_example(self):
        word, _ = WordCollectionMocups.create_word(self.user)
        example_data = {"sentence": "test sentence", "translation": "test translation"}
        response = self.client.post(
            f"/api/words/{word.id}/add_word_example/", example_data, format="json"
        )

        assert response.status_code == 201
        assert response.data["sentence"] == example_data["sentence"]
        assert response.data["translation"] == example_data["translation"]

        assert any(
            example.sentence == example_data["sentence"]
            and example.translation == example_data["translation"]
            for example in word.examples.all()
        )
    
    @pytest.mark.django_db
    def test_remove_word_example(self):
        word, _ = WordCollectionMocups.create_word(self.user)
        assert word.examples.exists()

        example = word.examples.first()
        response = self.client.delete(
            f"/api/words/{word.id}/remove_word_example/", {"item_id": example.id}, format="json"
        )

        assert response.status_code == 204
        assert not word.examples.filter(id=example.id).exists()
    
    @pytest.mark.django_db
    def test_add_word_translation(self):
        word, _ = WordCollectionMocups.create_word(self.user)
        translation_data = {"translation": "test translation"}
        response = self.client.post(
            f"/api/words/{word.id}/add_word_translation/", translation_data, format="json"
        )

        assert response.status_code == 201
        assert response.data["translation"] == translation_data["translation"]

        assert any(
            translation.translation == translation_data["translation"]
            for translation in word.translations.all()
        )
    
    @pytest.mark.django_db
    def test_remove_word_translation(self):
        word, _ = WordCollectionMocups.create_word(self.user)
        assert word.translations.exists()

        translation = word.translations.first()
        response = self.client.delete(
            f"/api/words/{word.id}/remove_word_translation/", {"item_id": translation.id}, format="json"
        )

        assert response.status_code == 204
        assert not word.translations.filter(id=translation.id).exists()

    @pytest.mark.django_db
    def test_add_word_preposition_and_case_with_translation(self):
        word, _ = WordCollectionMocups.create_word(self.user)
        data = {
            "preposition": "test preposition",
            "case": "test case",
            "translation": "test translation"
        }
        response = self.client.post(
            f"/api/words/{word.id}/add_word_preposition_and_case_with_translation/", data, format="json"
        )

        assert response.status_code == 201
        assert response.data["preposition"] == data["preposition"]
        assert response.data["case"] == data["case"]
        assert response.data["translation"] == data["translation"]

        assert any(
            pcwt.preposition == data["preposition"]
            and pcwt.case == data["case"]
            and pcwt.translation == data["translation"]
            for pcwt in word.prepositions_and_cases_with_translations.all())
        
    @pytest.mark.django_db
    def test_remove_word_preposition_and_case_with_translation(self):
        word, _ = WordCollectionMocups.create_word(self.user)
        assert word.prepositions_and_cases_with_translations.exists()

        item = word.prepositions_and_cases_with_translations.first()
        response = self.client.delete(
            f"/api/words/{word.id}/remove_word_preposition_and_case_with_translation/", {"item_id": item.id}, format="json"
        )

        assert response.status_code == 204
        assert not word.prepositions_and_cases_with_translations.filter(id=item.id).exists()

from rest_framework import serializers

from .models import (
    Collection,
    Word,
    Tag,
    WordForm,
    WordExample,
    WordTranslation,
    WordPrepositionAndCaseWithTranslation,
)

class TagSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = Tag
        fields = ["owner", "id", "name"]

class CollectionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = ["owner", "id", "name", "description", "words", "tags", "image_url"]

class WordFormSerializer(serializers.ModelSerializer):
    word_id = serializers.IntegerField(source="word.id", read_only=True)

    class Meta:
        model = WordForm
        fields = ["id", "word_id", "name", "form"]


class WordExampleSerializer(serializers.ModelSerializer):
    word_id = serializers.IntegerField(source="word.id", read_only=True)

    class Meta:
        model = WordExample
        fields = ["id", "word_id", "sentence", "translation"]


class WordTranslationSerializer(serializers.ModelSerializer):
    word_id = serializers.IntegerField(source="word.id", read_only=True)

    class Meta:
        model = WordTranslation
        fields = ["id", "word_id", "translation"]


class WordPrepositionAndCaseWithTranslationSerializer(serializers.ModelSerializer):
    word_id = serializers.IntegerField(source="word.id", read_only=True)

    class Meta:
        model = WordPrepositionAndCaseWithTranslation
        fields = ["id", "word_id", "preposition", "case", "translation"]


class WordListSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")
    genus_name = serializers.CharField(source="get_genus_id_display")
    part_of_speech_name = serializers.CharField(source="get_part_of_speech_id_display")

    class Meta:
        model = Word
        fields = [
            "owner",
            "id",
            "created_date_time",
            "definition",
            "part_of_speech_id",
            "part_of_speech_name",
            "genus_id",
            "genus_name",
            "image_url",
        ]


class WordDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")
    genus_name = serializers.CharField(source="get_genus_id_display", read_only=True)
    part_of_speech_name = serializers.CharField(
        source="get_part_of_speech_id_display", read_only=True
    )
    translations = WordTranslationSerializer(many=True)
    examples = WordExampleSerializer(many=True)
    forms = WordFormSerializer(many=True)
    prepositions_and_cases_with_translations = (
        WordPrepositionAndCaseWithTranslationSerializer(many=True)
    )

    class Meta:
        model = Word
        fields = [
            "owner",
            "id",
            "created_date_time",
            "definition",
            "translations",
            "examples",
            "forms",
            "prepositions_and_cases_with_translations",
            "part_of_speech_id",
            "part_of_speech_name",
            "genus_id",
            "genus_name",
            "image_url",
        ]

    def create(self, validated_data):
        translations_data = validated_data.pop("translations", [])
        examples_data = validated_data.pop("examples", [])
        forms_data = validated_data.pop("forms", [])
        prepositions_data = validated_data.pop(
            "prepositions_and_cases_with_translations", []
        )

        word = super().create(validated_data)

        for translation_data in translations_data:
            WordTranslation.objects.create(word=word, **translation_data)
        for example_data in examples_data:
            WordExample.objects.create(word=word, **example_data)
        for form_data in forms_data:
            WordForm.objects.create(word=word, **form_data)
        for preposition_data in prepositions_data:
            WordPrepositionAndCaseWithTranslation.objects.create(
                word=word, **preposition_data
            )

        return word

    def update(self, instance, validated_data):
        translations_data = validated_data.pop("translations", serializers.empty)
        examples_data = validated_data.pop("examples", serializers.empty)
        forms_data = validated_data.pop("forms", serializers.empty)
        prepositions_data = validated_data.pop(
            "prepositions_and_cases_with_translations", serializers.empty
        )

        instance = super().update(instance, validated_data)

        if translations_data is not serializers.empty:
            instance.translations.all().delete()
            for translation_data in translations_data:
                WordTranslation.objects.create(word=instance, **translation_data)

        if examples_data is not serializers.empty:
            instance.examples.all().delete()
            for example_data in examples_data:
                WordExample.objects.create(word=instance, **example_data)

        if forms_data is not serializers.empty:
            instance.forms.all().delete()
            for form_data in forms_data:
                WordForm.objects.create(word=instance, **form_data)

        if prepositions_data is not serializers.empty:
            instance.prepositions_and_cases_with_translations.all().delete()
            for preposition_data in prepositions_data:
                WordPrepositionAndCaseWithTranslation.objects.create(
                    word=instance, **preposition_data
                )

        return instance

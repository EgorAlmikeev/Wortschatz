from rest_framework import serializers

from .models import (
    Word,
    Category,
    WordForm,
    WordExample,
    WordTranslation,
    WordPrepositionAndCaseWithTranslation,
)


class CategorySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = Category
        fields = ["owner", "id", "name", "color"]


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
    genus_name = serializers.CharField(source="get_genus_id_display", read_only=True)
    part_of_speech_name = serializers.CharField(
        source="get_part_of_speech_id_display", read_only=True
    )

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
    translations = WordTranslationSerializer(many=True, read_only=True)
    examples = WordExampleSerializer(many=True, read_only=True)
    forms = WordFormSerializer(many=True, read_only=True)
    prepositions_and_cases_with_translations = (
        WordPrepositionAndCaseWithTranslationSerializer(many=True, read_only=True)
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

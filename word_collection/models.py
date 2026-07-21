from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

from .mixins import OwnedModelMixin

class Collection(OwnedModelMixin, models.Model):
    # Name of the collection
    name = models.TextField(max_length=100)
    # Description of the collection
    description = models.TextField(max_length=200, null=True)
    # Words in the collection
    words = models.ManyToManyField("Word", related_name="collections")
    # Tags in the collection
    tags = models.ManyToManyField("Tag", related_name="collections")
    # Image URL for the collection
    image_url = models.TextField(max_length=200, null=True)
    # Hex color code
    background_color = models.TextField(max_length=7, null=True)

    def __str__(self):
        return self.name

class Tag(OwnedModelMixin, models.Model):
    # Name of the tag
    name = models.TextField(max_length=100)

    def __str__(self):
        return self.name

class Genus(models.IntegerChoices):
    MALE = 1, "Male"
    FEMALE = 2, "Female"
    NEUTRAL = 3, "Neutral"
    PLURAL = 4, "Plural"

class PartOfSpeech(models.IntegerChoices):
    NOUN = 1, "Noun"
    VERB = 2, "Verb"
    ADJECTIVE = 3, "Adjective"
    PRONOUN = 4, "Pronoun"
    ADVERB = 5, "Adverb"
    PREPOSITION = 6, "Preposition"
    NUMBER = 7, "Number"
    ARTICLE = 8, "Article"
    CONJUNCTION = 9, "Conjunction"
    INTERJECTION = 10, "Interjection"


class WordForm(models.Model):
    # The word to which this form belongs
    word = models.ForeignKey("Word", on_delete=models.CASCADE, related_name="forms")
    # Name of the form (e.g., "Plural", "Past Tense")
    name = models.TextField(max_length=100)
    # The form itself (e.g., "Houses", "Went")
    form = models.TextField(max_length=100)


class WordExample(models.Model):
    # The word to which this form belongs
    word = models.ForeignKey("Word", on_delete=models.CASCADE, related_name="examples")
    # Sentence using the word
    sentence = models.TextField(max_length=200)
    # Translation of the sentence
    translation = models.TextField(max_length=200)


class WordTranslation(models.Model):
    # The word to which this form belongs
    word = models.ForeignKey(
        "Word", on_delete=models.CASCADE, related_name="translations"
    )
    # The translation of the word
    translation = models.TextField(max_length=100)


class WordPrepositionAndCaseWithTranslation(models.Model):
    # The word to which this form belongs
    word = models.ForeignKey(
        "Word",
        on_delete=models.CASCADE,
        related_name="prepositions_and_cases_with_translations",
    )
    # Preposition
    preposition = models.TextField(max_length=100)
    # Case associated with the preposition
    case = models.TextField(max_length=100)
    # Translation of the preposition and case combination
    translation = models.TextField(max_length=100)


class Word(OwnedModelMixin, models.Model):
    # Date and time of creation
    created_date_time = models.DateTimeField(default=now)
    # Definition
    definition = models.TextField(max_length=100)
    # Genus for nouns
    genus_id = models.IntegerField(choices=Genus.choices, null=True)
    # Part of speech
    part_of_speech_id = models.IntegerField(choices=PartOfSpeech.choices, null=True)
    # URL of the image associated with the word
    image_url = models.TextField(max_length=200, null=True)

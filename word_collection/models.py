from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

from .mixins import OwnedModelMixin

class Category(OwnedModelMixin, models.Model):
    # Name of the category
    name = models.TextField(max_length=100)
    # Associated color in HEX format
    color = models.TextField(max_length=10, default="#EACB00")

    def __str__(self):
        return self.name

class Genus(models.IntegerChoices):
    MALE = 1, 'Male'
    FEMALE = 2, 'Female'
    NEUTRAL = 3, 'Neutral'
    PLURAL = 4, 'Plural'

class PartOfSpeech(models.IntegerChoices):
    NOUN = 1, 'Noun'
    VERB = 2, 'Verb'
    ADJECTIVE = 3, 'Adjective'
    PRONOUN = 4, 'Pronoun'
    ADVERB = 5, 'Adverb'
    PREPOSITION = 6, 'Preposition'
    NUMBER = 7, 'Number'
    ARTICLE = 8, 'Article'
    CONJUNCTION = 9, 'Conjunction'
    INTERJECTION = 10, 'Interjection'

class Word(OwnedModelMixin, models.Model):
    # Date and time of creation
    created_date_time = models.DateTimeField(default=now)
    # Definition
    definition = models.TextField(max_length=100)
    # List of translations
    translations = models.JSONField(default=list)
    # Use cases
    # [["Sentence", "Translation"], ...]
    examples = models.JSONField(default=list)
    # Other forms of the word
    # [["Name of the form", "The form itself"], ...]
    other_forms = models.JSONField(default=list)
    # Prepositions with their cases and translations
    # [["Preposition", "Case", "Translation"], ...]
    prepositions_and_cases_with_translations = models.JSONField(default=list)
    # Genus for nouns
    genus_id = models.IntegerField(choices=Genus.choices, null=True)
    # List of associated categories
    categories = models.ManyToManyField(Category, related_name='words')
    # Part of speech
    part_of_speech_id = models.IntegerField(choices=PartOfSpeech, null=True)
    # How many times the word has been used
    usage_count = models.PositiveIntegerField(default=0)

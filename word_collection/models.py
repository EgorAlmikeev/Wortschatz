from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

from .utils import get_superuser_id

class Category(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories", db_index=True, default=get_superuser_id)
    name = models.TextField(max_length=100)

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

class Word(models.Model):
    # Besitzer
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='words', db_index=True)
    # Erscheinungsdatum
    created_date_time = models.DateTimeField(default=now)
    # Definition
    definition = models.TextField(max_length=100)
    # Übersetzungsvarianten
    translations = models.JSONField(default=list)
    # Nutzungsvarianten
    # [["Variante", "Übersetzung"], ...]
    examples = models.JSONField(default=list)
    # Andere Formen
    # [["Formname", "Formdefinition"], ...]
    other_forms = models.JSONField(default=list)
    # Präpositionen und Fälle (für Verben)
    # [["Präposition", "Fall", "Übersetzung"], ...]
    prepositions_and_cases_with_translations = models.JSONField(default=list)
    # Geschlecht (für Nomen)
    genus_id = models.IntegerField(choices=Genus.choices, null=True)
    # Kategorien
    categories = models.ManyToManyField(Category, related_name='words')
    # Wortart
    part_of_speech_id = models.IntegerField(choices=PartOfSpeech, null=True)
    # Nutzungsanzahl
    usage_count = models.PositiveIntegerField(default=0)

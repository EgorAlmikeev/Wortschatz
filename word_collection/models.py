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
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='words', db_index=True)
    created_date_time = models.DateTimeField(default=now)
    definition = models.TextField(max_length=100)
    translation = models.TextField(max_length=100)
    example = models.TextField(max_length=200)
    genus_id = models.IntegerField(choices=Genus.choices, null=True)
    categories = models.ManyToManyField(Category, related_name='words')
    part_of_speech = models.IntegerField(choices=PartOfSpeech, null=True)
    usage_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.definition
from django.db import models
from datetime import datetime

class Theme(models.Model):
    name = models.TextField(max_length=100)

class Word(models.Model):
    class Genus(models.IntegerChoices):
        MALE = 1, 'Male'
        FEMALE = 2, 'Female'
        NEUTRAL = 3, 'Neutral'
        PLURAL = 4, 'Plural'

    created_date_time = models.DateTimeField(default=datetime.now())
    word = models.TextField(max_length=100)
    translation = models.TextField(max_length=100)
    example = models.TextField(max_length=200)
    genus = models.IntegerField(choices=Genus.choices, null=True)
    theme = models.ManyToManyField(Theme, related_name="words")
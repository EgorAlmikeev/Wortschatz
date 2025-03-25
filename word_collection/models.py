from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.TextField(max_length=100)

    def __str__(self):
        return self.name
    
class Genus(models.IntegerChoices):
    MALE = 1, 'Male'
    FEMALE = 2, 'Female'
    NEUTRAL = 3, 'Neutral'
    PLURAL = 4, 'Plural'

class Word(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="words", db_index=True)
    created_date_time = models.DateTimeField(default=now)
    definition = models.TextField(max_length=100)
    translation = models.TextField(max_length=100)
    example = models.TextField(max_length=200)
    genus_id = models.IntegerField(choices=Genus.choices, null=True)
    categories = models.ManyToManyField(Category, related_name="words")
    usage_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.definition
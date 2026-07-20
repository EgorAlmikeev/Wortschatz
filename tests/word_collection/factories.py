import factory
from faker import Faker

from word_collection.models import (
    Tag,
    Word,
    WordForm,
    WordExample,
    WordTranslation,
    WordPrepositionAndCaseWithTranslation,
)

"""
Payload factories for testing purposes.
These factories generate mock JSON DATA for API testing. 
"""


class TagPayloadFactory(factory.DictFactory):
    name = factory.Faker("word")

class CollectionPayloadFactory(factory.DictFactory):
    name = factory.Faker("word")
    description = factory.Faker("sentence", nb_words=10)
    image_url = factory.Faker("url")

class WordPayloadFactory(factory.DictFactory):
    definition = factory.Faker("word")
    genus_id = factory.Faker("random_int", min=1, max=4)
    part_of_speech_id = factory.Faker("random_int", min=1, max=10)
    image_url = factory.Faker("url")

    @factory.post_generation
    def translations(self, create, extracted, **kwargs):
        fake = Faker()
        translations = (
            extracted
            if extracted is not None
            else [{"translation": fake.word()} for _ in range(2)]
        )
        self["translations"] = translations

    @factory.post_generation
    def examples(self, create, extracted, **kwargs):
        fake = Faker()
        examples = (
            extracted
            if extracted is not None
            else [
                {
                    "sentence": fake.sentence(nb_words=6),
                    "translation": fake.word(),
                }
                for _ in range(2)
            ]
        )
        self["examples"] = examples

    @factory.post_generation
    def forms(self, create, extracted, **kwargs):
        fake = Faker()
        forms = (
            extracted
            if extracted is not None
            else [
                {
                    "name": fake.word(),
                    "form": fake.word(),
                }
                for _ in range(2)
            ]
        )
        self["forms"] = forms

    @factory.post_generation
    def prepositions_and_cases_with_translations(self, create, extracted, **kwargs):
        fake = Faker()
        items = (
            extracted
            if extracted is not None
            else [
                {
                    "preposition": fake.word(),
                    "case": fake.word(),
                    "translation": fake.word(),
                }
                for _ in range(2)
            ]
        )
        self["prepositions_and_cases_with_translations"] = items


"""
Model factories for testing purposes.
These factories generate mock model INSTANCES for testing.
"""


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Faker("word")

class CollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "word_collection.Collection"

    name = factory.Faker("word")
    description = factory.Faker("sentence", nb_words=10)
    image_url = factory.Faker("url")

class WordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Word
        skip_postgeneration_save = True

    definition = factory.Faker("word")
    genus_id = factory.Faker("random_int", min=1, max=4)
    part_of_speech_id = factory.Faker("random_int", min=1, max=10)
    image_url = factory.Faker("url")

    @factory.post_generation
    def translations(self, create, extracted, **kwargs):
        fake = Faker()
        translations = (
            extracted
            if extracted is not None
            else [{"translation": fake.word()} for _ in range(2)]
        )

        if create:
            for translation_data in translations:
                WordTranslation.objects.create(word=self, **translation_data)

    @factory.post_generation
    def examples(self, create, extracted, **kwargs):
        fake = Faker()
        examples = (
            extracted
            if extracted is not None
            else [
                {
                    "sentence": fake.sentence(nb_words=6),
                    "translation": fake.word(),
                }
                for _ in range(2)
            ]
        )

        if create:
            for example_data in examples:
                WordExample.objects.create(word=self, **example_data)

    @factory.post_generation
    def forms(self, create, extracted, **kwargs):
        fake = Faker()
        forms = (
            extracted
            if extracted is not None
            else [
                {
                    "name": fake.word(),
                    "form": fake.word(),
                }
                for _ in range(2)
            ]
        )

        if create:
            for form_data in forms:
                WordForm.objects.create(word=self, **form_data)

    @factory.post_generation
    def prepositions_and_cases_with_translations(self, create, extracted, **kwargs):
        fake = Faker()
        items = (
            extracted
            if extracted is not None
            else [
                {
                    "preposition": fake.word(),
                    "case": fake.word(),
                    "translation": fake.word(),
                }
                for _ in range(2)
            ]
        )

        if create:
            for item_data in items:
                WordPrepositionAndCaseWithTranslation.objects.create(
                    word=self, **item_data
                )

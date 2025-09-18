import factory
from faker import Faker

from word_collection.models import Category, Word

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker('word')

class WordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Word
        skip_postgeneration_save = True

    id = factory.Sequence(lambda n: n + 1)
    definition = factory.Faker('word')
    genus_id = factory.Faker('random_int', min=1, max=4)
    part_of_speech_id = factory.Faker('random_int', min=1, max=10)
    usage_count = factory.Faker('random_int', min=0, max=100)

    @factory.post_generation
    def translations(self, create, extracted, **kwargs):
        from faker import Faker
        fake = Faker()
        if extracted:
            self.translations = extracted
        else:
            self.translations = [fake.word() for _ in range(2)]
        
        if create:
            self.save()

    @factory.post_generation
    def examples(self, create, extracted, **kwargs):
        from faker import Faker
        fake = Faker()
        if extracted:
            self.examples = extracted
        else:
            self.examples = [[fake.word(), fake.word()] for _ in range(2)]
        
        if create:
            self.save()
    
    @factory.post_generation
    def other_forms(self, create, extracted, **kwargs):
        from faker import Faker
        fake = Faker()
        if extracted:
            self.other_forms = extracted
        else:
            self.other_forms = [[fake.word(), fake.word()] for _ in range(2)]
        
        if create:
            self.save()
    
    @factory.post_generation
    def prepositions_and_cases_with_translations(self, create, extracted, **kwargs):
        from faker import Faker
        fake = Faker()
        if extracted:
            self.prepositions_and_cases_with_translations = extracted
        else:
            self.prepositions_and_cases_with_translations = [[fake.word(), fake.word(), fake.word()] for _ in range(2)]
        
        if create:
            self.save()

from django.contrib.auth.models import User

from .models import Collection, Genus, PartOfSpeech, Tag, Word

# Starter vocabulary shown to every newly registered user so they can see how
# words, translations, examples, forms and prepositions fit together.
DEFAULT_WORDS = [
    {
        "definition": "Haus",
        "genus_id": Genus.NEUTRAL,
        "part_of_speech_id": PartOfSpeech.NOUN,
        "image_url": "https://placehold.co/300x300?text=Haus",
        "translations": [{"translation": "house"}],
        "examples": [
            {"sentence": "Das Haus ist groß.", "translation": "The house is big."}
        ],
        "forms": [{"name": "Plural", "form": "Häuser"}],
        "prepositions_and_cases_with_translations": [
            {
                "preposition": "in",
                "case": "Dativ",
                "translation": "in the house (location)",
                "example": "Wir sind im Haus.",
            }
        ],
    },
    {
        "definition": "Katze",
        "genus_id": Genus.FEMALE,
        "part_of_speech_id": PartOfSpeech.NOUN,
        "image_url": "https://placehold.co/300x300?text=Katze",
        "translations": [{"translation": "cat"}],
        "examples": [
            {
                "sentence": "Die Katze schläft auf dem Sofa.",
                "translation": "The cat is sleeping on the sofa.",
            }
        ],
        "forms": [{"name": "Plural", "form": "Katzen"}],
        "prepositions_and_cases_with_translations": [
            {
                "preposition": "mit",
                "case": "Dativ",
                "translation": "with the cat",
                "example": "Ich spiele mit der Katze.",
            }
        ],
    },
    {
        "definition": "Hund",
        "genus_id": Genus.MALE,
        "part_of_speech_id": PartOfSpeech.NOUN,
        "image_url": "https://placehold.co/300x300?text=Hund",
        "translations": [{"translation": "dog"}],
        "examples": [
            {
                "sentence": "Der Hund läuft im Park.",
                "translation": "The dog is running in the park.",
            }
        ],
        "forms": [{"name": "Plural", "form": "Hunde"}],
        "prepositions_and_cases_with_translations": [
            {
                "preposition": "ohne",
                "case": "Akkusativ",
                "translation": "without the dog",
                "example": "Ich gehe nie ohne den Hund spazieren.",
            }
        ],
    },
    {
        "definition": "Buch",
        "genus_id": Genus.NEUTRAL,
        "part_of_speech_id": PartOfSpeech.NOUN,
        "image_url": "https://placehold.co/300x300?text=Buch",
        "translations": [{"translation": "book"}],
        "examples": [
            {
                "sentence": "Ich lese ein interessantes Buch.",
                "translation": "I am reading an interesting book.",
            }
        ],
        "forms": [{"name": "Plural", "form": "Bücher"}],
        "prepositions_and_cases_with_translations": [
            {
                "preposition": "über",
                "case": "Akkusativ",
                "translation": "about the book (topic)",
                "example": "Wir sprechen über das Buch.",
            }
        ],
    },
    {
        "definition": "Tisch",
        "genus_id": Genus.MALE,
        "part_of_speech_id": PartOfSpeech.NOUN,
        "image_url": "https://placehold.co/300x300?text=Tisch",
        "translations": [{"translation": "table"}],
        "examples": [
            {
                "sentence": "Das Essen steht auf dem Tisch.",
                "translation": "The food is on the table.",
            }
        ],
        "forms": [{"name": "Plural", "form": "Tische"}],
        "prepositions_and_cases_with_translations": [
            {
                "preposition": "auf",
                "case": "Dativ",
                "translation": "on the table (location)",
                "example": "Das Essen steht auf dem Tisch.",
            }
        ],
    },
]


def create_default_collection(owner: User) -> Collection:
    """Seed a fully-populated starter collection for a newly registered user."""
    tag = Tag.objects.create(owner=owner, name="Beginner")

    collection = Collection.objects.create(
        owner=owner,
        name="My First Collection",
        description=(
            "A starter set of essential German words to help you get "
            "familiar with Wortschatz."
        ),
        image_url="https://placehold.co/600x400?text=My+Collection",
        background_color="#4A90D9",
    )
    collection.tags.add(tag)

    for word_data in DEFAULT_WORDS:
        word = Word.objects.create(
            owner=owner,
            definition=word_data["definition"],
            genus_id=word_data["genus_id"],
            part_of_speech_id=word_data["part_of_speech_id"],
            image_url=word_data["image_url"],
        )
        for translation in word_data["translations"]:
            word.translations.create(**translation)
        for example in word_data["examples"]:
            word.examples.create(**example)
        for form in word_data["forms"]:
            word.forms.create(**form)
        for preposition in word_data["prepositions_and_cases_with_translations"]:
            word.prepositions_and_cases_with_translations.create(**preposition)

        collection.words.add(word)

    return collection

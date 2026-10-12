from django.contrib.auth.models import User

from .models import Collection, Genus, PartOfSpeech, Tag, Word

# Starter vocabulary shown to every newly registered user: one word per part
# of speech, each filled in as richly as that part of speech allows, so a new
# user can see translations, examples, forms and preposition/case pairs all
# in action right away.
DEFAULT_WORDS = [
    {
        "definition": "Haus",
        "genus_id": Genus.NEUTRAL,
        "part_of_speech_id": PartOfSpeech.NOUN,
        "image_url": "https://placehold.co/300x300?text=Haus",
        "translations": [{"translation": "house"}, {"translation": "home"}],
        "examples": [
            {"sentence": "Das Haus ist groß.", "translation": "The house is big."},
            {
                "sentence": "Wir bauen ein neues Haus.",
                "translation": "We are building a new house.",
            },
        ],
        "forms": [
            {"name": "Plural", "form": "Häuser"},
            {"name": "Genitiv Singular", "form": "Hauses"},
        ],
        "prepositions_and_cases_with_translations": [
            {
                "preposition": "in",
                "case": "Dativ",
                "translation": "in the house (location)",
                "example": "Wir sind im Haus.",
            },
            {
                "preposition": "aus",
                "case": "Dativ",
                "translation": "from the house",
                "example": "Sie kommt aus dem Haus.",
            },
        ],
    },
    {
        "definition": "gehen",
        "genus_id": None,
        "part_of_speech_id": PartOfSpeech.VERB,
        "image_url": "https://placehold.co/300x300?text=gehen",
        "translations": [{"translation": "to go"}, {"translation": "to walk"}],
        "examples": [
            {"sentence": "Ich gehe zur Schule.", "translation": "I go to school."},
            {
                "sentence": "Wir gehen ins Kino.",
                "translation": "We are going to the cinema.",
            },
        ],
        "forms": [
            {"name": "Präsens (ich)", "form": "gehe"},
            {"name": "Präteritum (ich)", "form": "ging"},
            {"name": "Perfekt (ich)", "form": "bin gegangen"},
        ],
        "prepositions_and_cases_with_translations": [
            {
                "preposition": "zu",
                "case": "Dativ",
                "translation": "to go to",
                "example": "Ich gehe zum Arzt.",
            },
            {
                "preposition": "in",
                "case": "Akkusativ",
                "translation": "to go into",
                "example": "Er geht ins Haus.",
            },
        ],
    },
    {
        "definition": "glücklich",
        "genus_id": None,
        "part_of_speech_id": PartOfSpeech.ADJECTIVE,
        "image_url": "https://placehold.co/300x300?text=gluecklich",
        "translations": [{"translation": "happy"}, {"translation": "lucky"}],
        "examples": [
            {"sentence": "Sie ist sehr glücklich.", "translation": "She is very happy."}
        ],
        "forms": [
            {"name": "Komparativ", "form": "glücklicher"},
            {"name": "Superlativ", "form": "am glücklichsten"},
        ],
        "prepositions_and_cases_with_translations": [
            {
                "preposition": "über",
                "case": "Akkusativ",
                "translation": "happy about",
                "example": "Ich bin glücklich über die gute Nachricht.",
            }
        ],
    },
    {
        "definition": "ich",
        "genus_id": None,
        "part_of_speech_id": PartOfSpeech.PRONOUN,
        "image_url": "https://placehold.co/300x300?text=ich",
        "translations": [{"translation": "I"}, {"translation": "me (as subject)"}],
        "examples": [{"sentence": "Ich bin müde.", "translation": "I am tired."}],
        "forms": [
            {"name": "Akkusativ", "form": "mich"},
            {"name": "Dativ", "form": "mir"},
        ],
        "prepositions_and_cases_with_translations": [],
    },
    {
        "definition": "oft",
        "genus_id": None,
        "part_of_speech_id": PartOfSpeech.ADVERB,
        "image_url": "https://placehold.co/300x300?text=oft",
        "translations": [{"translation": "often"}, {"translation": "frequently"}],
        "examples": [
            {
                "sentence": "Ich gehe oft ins Kino.",
                "translation": "I often go to the cinema.",
            }
        ],
        "forms": [
            {"name": "Komparativ", "form": "öfter"},
            {"name": "Superlativ", "form": "am häufigsten"},
        ],
        "prepositions_and_cases_with_translations": [],
    },
    {
        "definition": "auf",
        "genus_id": None,
        "part_of_speech_id": PartOfSpeech.PREPOSITION,
        "image_url": "https://placehold.co/300x300?text=auf",
        "translations": [{"translation": "on"}, {"translation": "onto"}],
        "examples": [
            {
                "sentence": "Die Lampe steht auf dem Tisch.",
                "translation": "The lamp is on the table.",
            }
        ],
        "forms": [],
        "prepositions_and_cases_with_translations": [
            {
                "preposition": "auf",
                "case": "Dativ",
                "translation": "on (location)",
                "example": "Das Buch liegt auf dem Tisch.",
            },
            {
                "preposition": "auf",
                "case": "Akkusativ",
                "translation": "onto (direction)",
                "example": "Ich lege das Buch auf den Tisch.",
            },
        ],
    },
    {
        "definition": "drei",
        "genus_id": None,
        "part_of_speech_id": PartOfSpeech.NUMBER,
        "image_url": "https://placehold.co/300x300?text=drei",
        "translations": [{"translation": "three"}],
        "examples": [
            {
                "sentence": "Ich habe drei Geschwister.",
                "translation": "I have three siblings.",
            }
        ],
        "forms": [{"name": "Ordinalzahl", "form": "dritte"}],
        "prepositions_and_cases_with_translations": [],
    },
    {
        "definition": "der",
        "genus_id": None,
        "part_of_speech_id": PartOfSpeech.ARTICLE,
        "image_url": "https://placehold.co/300x300?text=der",
        "translations": [{"translation": "the (masculine, nominative)"}],
        "examples": [
            {"sentence": "Der Hund läuft schnell.", "translation": "The dog runs fast."}
        ],
        "forms": [
            {"name": "Akkusativ", "form": "den"},
            {"name": "Dativ", "form": "dem"},
            {"name": "Genitiv", "form": "des"},
        ],
        "prepositions_and_cases_with_translations": [],
    },
    {
        "definition": "und",
        "genus_id": None,
        "part_of_speech_id": PartOfSpeech.CONJUNCTION,
        "image_url": "https://placehold.co/300x300?text=und",
        "translations": [{"translation": "and"}],
        "examples": [
            {"sentence": "Ich mag Kaffee und Tee.", "translation": "I like coffee and tea."}
        ],
        "forms": [],
        "prepositions_and_cases_with_translations": [],
    },
    {
        "definition": "Hallo",
        "genus_id": None,
        "part_of_speech_id": PartOfSpeech.INTERJECTION,
        "image_url": "https://placehold.co/300x300?text=Hallo",
        "translations": [{"translation": "hello"}, {"translation": "hi"}],
        "examples": [
            {
                "sentence": "Hallo, wie geht es dir?",
                "translation": "Hello, how are you?",
            }
        ],
        "forms": [],
        "prepositions_and_cases_with_translations": [],
    },
]


def create_default_collection(owner: User) -> Collection:
    """Seed a fully-populated starter collection for a newly registered user."""
    tag = Tag.objects.create(owner=owner, name="Beginner")

    collection = Collection.objects.create(
        owner=owner,
        name="My First Collection",
        description=(
            "A starter set of German words — one for every part of speech — "
            "to help you see everything Wortschatz can do."
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

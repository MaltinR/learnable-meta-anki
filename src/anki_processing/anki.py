import genanki

MODEL_ID = 1572187907

MODEL = genanki.Model(
    MODEL_ID,
    "Model",
    fields=[
        {"name": "Question"},
        {"name": "Answer"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{Question}}",
            "afmt": "{{FrontSide}}<hr id='answer'>{{Answer}}",
        },
    ],
)

def to_deck(name: str, notes: list[genanki.Note]) -> genanki.Deck:
    deck = genanki.Deck(
        gen_id(),
        name,
    )

    for note in notes:
        deck.add_note(note)

    return deck

def images_to_question(images: list[str]) -> str:
    return "\n".join([f'<img src="{image}">' for image in images])

def to_note(question: str, answer: str) -> genanki.Note:
    return genanki.Note(MODEL, [question, answer])

def gen_id() -> int:
    import random
    return random.randrange(1 << 30, 1 << 31)

def export_package(deck: genanki.Deck, images: list[str], package_path: str):
    package = genanki.Package(deck)
    package.media_files = images
    package.write_to_file(package_path)
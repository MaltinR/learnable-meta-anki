import os
import argparse
import tempfile
from pydantic import BaseModel
from pathlib import Path
from uuid import uuid4
import genanki
from src.domain.meta import Meta
from src.source_processing import learnable_meta
from src.anki_processing import anki

OUTPUT_DIR = "./output"

class MetaList(BaseModel):
    metas: list[Meta]

def normalize_package_name(package_name: str) -> str:
    import re
    snake = re.sub(r"\s+", "-", package_name.strip().lower().replace("-", ""))
    return snake + ".apkg"

def download_map(map_id):
    html = learnable_meta.download_map(map_id)
    name, author = learnable_meta.extract_name_author(html)
    result = learnable_meta.extract_meta_list(html)
    simplified = learnable_meta.simplify_meta_list(result)

    with tempfile.TemporaryDirectory() as tmp:
        images: list[str] = []
        notes: list[genanki.Note] = []
        for meta in simplified:
            meta_images: list[tuple[str, bytes, str]] = []
            try:
                for image in meta.images:
                    image_bytes = learnable_meta.download_image(image)
                    file_extension = learnable_meta.get_image_url_extension(image)
                    file_name = f"{uuid4()}{file_extension}"
                    image_path = Path(tmp) / file_name
                    image_path.write_bytes(image_bytes)

                    meta_images.append((str(image_path), image_bytes, file_name))

                for meta_image in meta_images: 
                    images.append(meta_image[0])

                question = anki.images_to_question([meta_image[2] for meta_image in meta_images])
                notes.append(anki.to_note(question, meta.note))
                
            except:
                continue
        deck_name = f"{name} by {author}"
        deck = anki.to_deck(deck_name, notes)
        package_path = Path(os.path.join(OUTPUT_DIR, normalize_package_name(deck_name)))
        package_path.parent.mkdir(parents=True, exist_ok=True)
        anki.export_package(deck, images, str(package_path))
        print(f"successfully export package '{deck_name}' to '{package_path}'")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("map_id")

    args = parser.parse_args()

    download_map(args.map_id)

if __name__ == "__main__":
    main()

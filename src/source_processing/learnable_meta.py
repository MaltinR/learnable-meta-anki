import json
import re
from src.domain.meta import Meta

def simplify_meta_list(meta_list: list[dict]) -> list[Meta]:
    return [
        Meta(
            name=meta["name"],
            note=meta["note"],
            images=meta["images"],
        )
        for meta in meta_list
    ]

def extract_name_author(html: str) -> tuple[str, str]:
    name_match = re.search(r'\bmapName\s*:\s*"([^"]*)"', html)
    author_match = re.search(r'\bmapAuthors\s*:\s*"([^"]*)"', html)

    if not name_match:
        raise ValueError("mapName not found")
    if not author_match:
        raise ValueError("mapAuthors not found")

    return name_match.group(1), author_match.group(1)

def extract_meta_list(html: str) -> list[dict]:
    # Find the beginning of metaList
    match = re.search(r"\bmetaList\s*:\s*", html)
    if not match:
        raise ValueError("metaList not found")

    start = match.end()

    # Find the matching closing ] while respecting strings/nesting
    depth = 0
    in_string = False
    escape = False
    quote = None

    for i in range(start, len(html)):
        c = html[i]

        if in_string:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == quote:
                in_string = False
            continue

        if c in ('"', "'"):
            in_string = True
            quote = c
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                raw = html[start:i + 1]
                break
    else:
        raise ValueError("Could not find end of metaList")

    # Quote unquoted JS object keys:
    # { id: 159, name: "foo" }
    # -> { "id": 159, "name": "foo" }
    raw = re.sub(
        r'([{,]\s*)([A-Za-z_$][A-Za-z0-9_$]*)\s*:',
        r'\1"\2":',
        raw,
    )

    return json.loads(raw)

def download_map(map_id: str) -> str:
    import requests
    base_url = "https://learnablemeta.com/maps/"
    url = base_url + map_id
    res = requests.get(url)
    return res.text

def download_image(url: str) -> bytes:
    import requests
    res = requests.get(url)
    return res.content

def get_image_url_extension(url: str) -> str:
    from pathlib import Path
    from urllib.parse import urlparse

    extension = Path(urlparse(url).path).suffix

    return extension
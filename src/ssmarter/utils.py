import json, os, re, textwrap
from pathlib import Path
from datetime import datetime

SAFE_CHARS = re.compile(r"[^a-zA-Z0-9._-]+")

def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, data):
    ensure_dir(str(Path(path).parent))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def slugify(text: str) -> str:
    return SAFE_CHARS.sub("-", text.lower()).strip("-")[:80] or "short"

def now_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d-%H%M%S")

def wrap_words(text: str, width: int = 32):
    return textwrap.wrap(text, width=width)

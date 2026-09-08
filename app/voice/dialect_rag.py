import json
import re
from pathlib import Path
from rapidfuzz import process, fuzz


BASE_DIR = Path(__file__).resolve().parent
RAG_PATH = BASE_DIR / "vocabulary_rag.jsonl"


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    text = text.lower()
    return re.findall(r"[ա-ֆև]+", text, flags=re.UNICODE)


def load_dialect_entries() -> list[dict]:
    entries = []

    if not RAG_PATH.exists():
        return entries

    with open(RAG_PATH, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue

            word = item.get("word")
            meaning = item.get("meaning")
            text = item.get("text")

            if not word:
                continue

            entries.append(
                {
                    "id": item.get("id"),
                    "word": str(word).strip().lower(),
                    "meaning": str(meaning).strip() if meaning else "",
                    "category": item.get("category"),
                    "region": item.get("region"),
                    "text": str(text).strip() if text else "",
                }
            )

    return entries


DIALECT_ENTRIES = load_dialect_entries()
DIALECT_WORDS = [entry["word"] for entry in DIALECT_ENTRIES]
DIALECT_BY_WORD = {entry["word"]: entry for entry in DIALECT_ENTRIES}


def find_dialect_words(text: str, fuzzy_threshold: int = 88) -> list[dict]:
    """
    Finds dialect / slang words in recognized Armenian text.
    Does not replace the text. It only returns explanations.
    """

    if not text:
        return []

    tokens = tokenize(text)
    found = {}

    for token in tokens:
        # Exact match
        if token in DIALECT_BY_WORD:
            found[token] = DIALECT_BY_WORD[token]
            continue

        # Fuzzy match
        if len(token) >= 4 and DIALECT_WORDS:
            match = process.extractOne(
                token,
                DIALECT_WORDS,
                scorer=fuzz.ratio,
            )

            if match:
                candidate, score, _ = match

                if score >= fuzzy_threshold:
                    found[candidate] = {
                        **DIALECT_BY_WORD[candidate],
                        "matched_from": token,
                        "score": score,
                    }

    return list(found.values())


def build_dialect_context(text: str) -> str:
    matches = find_dialect_words(text)

    if not matches:
        return ""

    lines = []

    for item in matches:
        word = item.get("word", "")
        meaning = item.get("meaning", "")
        region = item.get("region") or "չնշված"

        lines.append(
            f"- {word}: {meaning}. Տարածաշրջան՝ {region}"
        )

    return "\n".join(lines)
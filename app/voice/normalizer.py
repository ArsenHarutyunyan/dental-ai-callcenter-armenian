import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
VOCAB_PATH = BASE_DIR / "vocabulary.json"


def load_vocabulary() -> dict:
    if not VOCAB_PATH.exists():
        return {}

    with open(VOCAB_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        return {}

    return {
        str(k).strip().lower(): str(v).strip()
        for k, v in data.items()
        if str(k).strip() and str(v).strip()
    }


VOCABULARY = load_vocabulary()


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def safe_replace_word_or_phrase(text: str, wrong: str, correct: str) -> str:
    """
    Replaces only full words / phrases.
    Prevents bugs like:
    գրան + ցեք -> գրանցելցեք
    """

    pattern = r"(?<![\w])" + re.escape(wrong) + r"(?![\w])"
    return re.sub(pattern, correct, text, flags=re.UNICODE)


def clean_grammar_noise(text: str) -> str:
    # remove standalone noisy "ե"
    text = re.sub(r"(?<![\w])ե(?![\w])", " ", text, flags=re.UNICODE)

    # common cleanup
    text = text.replace("գրանցել կամ խորհրդատվության", "գրանցել կամ խորհրդատվության")
    text = text.replace("կամ խորհրդատվության", "կամ խորհրդատվության համար")

    text = normalize_spaces(text)
    return text


def normalize_text(text: str) -> str:
    if not text:
        return ""

    normalized = normalize_spaces(text.lower())

    for wrong, correct in sorted(
        VOCABULARY.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        normalized = safe_replace_word_or_phrase(normalized, wrong, correct)

    normalized = clean_grammar_noise(normalized)
    normalized = normalize_spaces(normalized)

    return normalized
def correct_armenian_text(text: str) -> str:
    """
    Safe corrector.

    Do not make aggressive corrections here.
    STT mistakes are handled in normalizer.py.
    """
    return text.strip() if text else ""
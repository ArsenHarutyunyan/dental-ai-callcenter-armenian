import wave
from pathlib import Path

from piper import PiperVoice

BASE_DIR = Path(__file__).resolve().parent
VOICE_PATH = BASE_DIR / "models" / "piper_hy" / "hy_AM-gor-medium.onnx"

_voice = None


def load_voice() -> PiperVoice:
    global _voice

    if _voice is None:
        print(f"Loading Armenian TTS voice: {VOICE_PATH}")
        _voice = PiperVoice.load(str(VOICE_PATH))
        print("TTS voice loaded")

    return _voice


def text_to_speech(text: str, output_file: str) -> str:
    """Fully offline Armenian TTS (Piper, hy_AM voice). Writes a WAV file
    and returns its path."""
    if not text:
        raise ValueError("text_to_speech: empty text")

    voice = load_voice()

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(output_path), "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    return str(output_path)

import os
import re
from pathlib import Path

import soundfile as sf
import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor

from app.voice.audio_preprocess import preprocess_audio

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models" / "whisper_turbo_hy"
SAMPLE_RATE = 16000
CHUNK_SECONDS = 28  # Whisper's own window is 30s; stay under it with margin
OVERLAP_SECONDS = 1

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("PYTORCH_MPS_HIGH_WATERMARK_RATIO", "0.0")

_processor = None
_model = None
_device = None


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def get_device() -> torch.device:
    global _device

    if _device is None:
        _device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    return _device


def load_model():
    global _processor, _model

    if _processor is None or _model is None:
        print(f"Loading Armenian STT model: {MODEL_DIR}")

        _processor = WhisperProcessor.from_pretrained(
            str(MODEL_DIR), language="hy", task="transcribe"
        )
        # eager attention: SDPA leaks memory on MPS over many generate() calls
        _model = WhisperForConditionalGeneration.from_pretrained(
            str(MODEL_DIR), dtype=torch.float32, attn_implementation="eager"
        )

        device = get_device()
        _model.to(device)
        _model.eval()
        _model.generation_config.language = "hy"
        _model.generation_config.task = "transcribe"
        _model.generation_config.forced_decoder_ids = None

        print(f"STT model loaded on: {device}")

    return _processor, _model


def transcribe_chunk(audio_chunk) -> str:
    processor, model = load_model()
    device = get_device()

    inputs = processor.feature_extractor(
        audio_chunk,
        sampling_rate=SAMPLE_RATE,
        return_tensors="pt",
    ).input_features.to(device)

    with torch.no_grad():
        ids = model.generate(inputs, max_new_tokens=200, language="hy", task="transcribe")

    if device.type == "mps":
        torch.mps.empty_cache()

    text = processor.tokenizer.batch_decode(ids, skip_special_tokens=True)[0]

    return normalize_spaces(text)


def split_audio(audio):
    chunk_size = CHUNK_SECONDS * SAMPLE_RATE
    overlap_size = OVERLAP_SECONDS * SAMPLE_RATE

    if len(audio) <= chunk_size:
        return [audio]

    chunks = []
    start = 0

    while start < len(audio):
        end = start + chunk_size
        chunk = audio[start:end]

        if len(chunk) > SAMPLE_RATE:
            chunks.append(chunk)

        if end >= len(audio):
            break

        start = end - overlap_size

    return chunks


def transcribe_audio(audio_path: str) -> str:
    path = Path(audio_path)

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path.resolve()}")

    clean_audio_path = preprocess_audio(str(path))

    audio, _ = sf.read(clean_audio_path, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    if audio is None or len(audio) == 0:
        return ""

    chunks = split_audio(audio)

    parts = []

    for index, chunk in enumerate(chunks, start=1):
        print(f"Transcribing chunk {index}/{len(chunks)}")
        text = transcribe_chunk(chunk)

        if text:
            parts.append(text)

    result = " ".join(parts)
    result = normalize_spaces(result)

    return result

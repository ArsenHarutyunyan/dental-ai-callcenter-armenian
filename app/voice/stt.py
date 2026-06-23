from faster_whisper import WhisperModel

model = WhisperModel(
    "large-v3",
    device="cpu",
    compute_type="int8",
)


def transcribe_audio(audio_path: str):
    segments, info = model.transcribe(
        audio_path,
        language="hy",
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=False,
    )

    return " ".join(segment.text.strip() for segment in segments).strip()
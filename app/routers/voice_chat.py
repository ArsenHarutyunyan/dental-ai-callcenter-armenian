import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.routers.chat import ChatRequest, chat
from app.voice.corrector import correct_armenian_text
from app.voice.normalizer import normalize_text
from app.voice.stt import transcribe_audio
from app.voice.tts import text_to_speech

router = APIRouter(prefix="/voice-chat", tags=["Voice Chat"])

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
async def voice_chat(
    clinic_id: int = Form(...),
    session_id: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Full offline voice turn: audio in -> STT -> local LLM agent -> TTS.
    Returns recognized/answer text plus an id to fetch the spoken reply with
    GET /voice-chat/audio/{audio_id}."""
    upload_id = uuid.uuid4().hex
    in_path = CACHE_DIR / f"in_{upload_id}.wav"
    in_path.write_bytes(await audio.read())

    recognized_text = transcribe_audio(str(in_path))
    corrected_text = correct_armenian_text(recognized_text)
    normalized_text = normalize_text(corrected_text)

    chat_result = chat(
        ChatRequest(clinic_id=clinic_id, session_id=session_id, message=normalized_text),
        db,
    )

    answer = chat_result.get("answer", "")
    audio_id = uuid.uuid4().hex
    out_path = CACHE_DIR / f"out_{audio_id}.wav"

    if answer:
        text_to_speech(answer, str(out_path))

    return {
        "recognized_text": recognized_text,
        "normalized_text": normalized_text,
        "chat_result": chat_result,
        "audio_id": audio_id if answer else None,
    }


@router.get("/audio/{audio_id}")
def get_voice_reply(audio_id: str):
    path = CACHE_DIR / f"out_{audio_id}.wav"
    return FileResponse(str(path), media_type="audio/wav")

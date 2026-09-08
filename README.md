# Dental AI Call Center — Armenian, fully offline

A local voice AI receptionist for dental clinics. A patient calls, speaks
Armenian, and the system understands the intent, answers questions from the
clinic's knowledge base, checks doctor availability, and books an appointment
— entirely on-device, no cloud APIs involved anywhere in the voice path.

**This is a portfolio snapshot, not a runnable package.** The fine-tuned
speech model and TTS voice weights are intentionally not included in this
repository (multi-gigabyte binaries, plus see `LICENSE`). This is here to
show the approach and the code, not to be cloned and deployed.

## Pipeline

```
caller audio
    │
    ▼
┌─────────────────────┐   Armenian speech → text
│ STT                 │   Whisper large-v3-turbo, LoRA fine-tuned on
│ app/voice/stt.py     │   ~108h of Armenian speech (crowdsourced +
│                      │   audiobooks + FLEURS + Artsakh dialect),
│                      │   running locally on Apple Silicon (MPS)
└─────────┬────────────┘
          │ recognized text
          ▼
┌─────────────────────┐   corrects known STT mistakes,
│ Corrector/Normalizer │   flags dialect/slang terms
│ app/voice/*.py        │
└─────────┬────────────┘
          │ clean text
          ▼
┌─────────────────────┐   intent detection + structured response,
│ Agent (local LLM)    │   grounded in clinic knowledge base, doctor
│ app/ai/agent.py       │   schedules and patient history — via Ollama
│                      │   (qwen3:4b), no data leaves the machine
└─────────┬────────────┘
          │ intent + Armenian answer (JSON)
          ▼
┌─────────────────────┐   FAQ answer, or slot lookup, or a new
│ CRM / booking logic  │   appointment written to Postgres
│ app/routers/*.py      │
└─────────┬────────────┘
          │ answer text
          ▼
┌─────────────────────┐   text → speech, Armenian (hy_AM) voice,
│ TTS                  │   Piper, on-device
│ app/voice/tts.py      │
└─────────┬────────────┘
          │
          ▼
     spoken reply
```

One HTTP call ties it together: `POST /voice-chat/` takes the caller's
audio and returns the recognized text, the structured agent decision, and
an id to fetch the synthesized voice reply from `GET /voice-chat/audio/{id}`.

## What's actually running locally

| Stage | Model | Notes |
|---|---|---|
| STT | Whisper large-v3-turbo + LoRA (custom fine-tune) | WER ~21% / CER ~8.5% on a held-out multi-source Armenian test set; CER ~2% on the crowdsourced-speech subset |
| LLM | Qwen3 4B via Ollama | Structured JSON intent extraction, grounded in DB context, always answers in Armenian |
| TTS | Piper, `hy_AM` voice | Sub-second synthesis for a few seconds of speech |
| DB | PostgreSQL | Patients, doctors, services, schedules, appointments, chat history |

No Groq, no OpenAI, no network calls once the models are loaded — verified
by round-tripping synthesized speech back through the STT model and
comparing to the source text.

## Stack

FastAPI · SQLAlchemy · PostgreSQL · Ollama · Whisper / transformers · Piper
TTS · PyTorch (MPS) · ffmpeg

## Origin of the STT model

The Armenian speech model was fine-tuned from scratch as a separate
project: sourced and cleaned ~123 hours of Armenian speech across four
datasets (crowdsourced recordings, audiobooks, FLEURS, and an Artsakh
dialect corpus), caught and excluded a corrupted 65%-of-dataset source
(transcripts hard-truncated at 40 characters) before it could poison
training, then fine-tuned Whisper on Apple Silicon (MPS) — including
working around several MPS-specific memory bugs in PyTorch/transformers
along the way.

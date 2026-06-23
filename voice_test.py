from app.voice.stt import transcribe_audio
from app.voice.tts import text_to_speech

audio_path = "test.wav"

text = transcribe_audio(audio_path)

print("Recognized text:")
print(text)

answer = "Բարև ձեզ, ինչպես կարող եմ օգնել։"

text_to_speech(answer, "response.mp3")

print("Response saved to response.mp3")
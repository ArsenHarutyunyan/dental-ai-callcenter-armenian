import re
import sys
from pathlib import Path

from app.voice.corrector import correct_armenian_text
from app.voice.normalizer import normalize_text
from app.voice.stt import transcribe_audio


def normalize_for_metric(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[։,՝՞՛՜.!?;:()\[\]\"']", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def word_error_rate(reference: str, hypothesis: str) -> float:
    ref_words = normalize_for_metric(reference).split()
    hyp_words = normalize_for_metric(hypothesis).split()

    n = len(ref_words)
    m = len(hyp_words)

    if n == 0:
        return 0.0 if m == 0 else 1.0

    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = i

    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if ref_words[i - 1] == hyp_words[j - 1] else 1

            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost,
            )

    return dp[n][m] / n


def evaluate_one(audio_path: Path, transcript_path: Path):
    reference = transcript_path.read_text(encoding="utf-8").strip()

    recognized = transcribe_audio(str(audio_path))
    corrected = correct_armenian_text(recognized)
    normalized = normalize_text(corrected)

    wer_raw = word_error_rate(reference, recognized)
    wer_norm = word_error_rate(reference, normalized)

    print("\n================================")
    print(f"Audio: {audio_path}")
    print("================================")

    print("\nReference:")
    print(reference)

    print("\nRecognized:")
    print(recognized)

    print("\nNormalized:")
    print(normalized)

    print(f"\nWER raw:  {wer_raw:.2%}")
    print(f"WER norm: {wer_norm:.2%}")

    return wer_raw, wer_norm


def main():
    audio_dir = Path("data/train/audio")
    transcript_dir = Path("data/train/transcripts")

    if not audio_dir.exists():
        raise FileNotFoundError(f"Missing folder: {audio_dir}")

    if not transcript_dir.exists():
        raise FileNotFoundError(f"Missing folder: {transcript_dir}")

    audio_files = sorted(
        list(audio_dir.glob("*.wav"))
        + list(audio_dir.glob("*.m4a"))
        + list(audio_dir.glob("*.mp3"))
    )

    if not audio_files:
        print("No audio files found.")
        sys.exit(1)

    scores_raw = []
    scores_norm = []

    for audio_path in audio_files:
        transcript_path = transcript_dir / f"{audio_path.stem}.txt"

        if not transcript_path.exists():
            print(f"Skipping {audio_path.name}: transcript missing")
            continue

        wer_raw, wer_norm = evaluate_one(audio_path, transcript_path)
        scores_raw.append(wer_raw)
        scores_norm.append(wer_norm)

    if scores_raw:
        avg_raw = sum(scores_raw) / len(scores_raw)
        avg_norm = sum(scores_norm) / len(scores_norm)

        print("\n==============================")
        print("FINAL RESULT")
        print("==============================")
        print(f"Files tested: {len(scores_raw)}")
        print(f"Average WER raw:  {avg_raw:.2%}")
        print(f"Average WER norm: {avg_norm:.2%}")


if __name__ == "__main__":
    main()
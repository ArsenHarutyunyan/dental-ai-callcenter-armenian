import subprocess
from pathlib import Path


SAMPLE_RATE = 16000


def preprocess_audio(input_path: str, output_path: str | None = None) -> str:
    """
    Converts any audio file to clean 16kHz mono WAV.

    This improves STT stability:
    - mono
    - 16 kHz
    - volume normalization
    - removes very low / very high noise
    """

    source = Path(input_path)

    if not source.exists():
        raise FileNotFoundError(f"Audio file not found: {source.resolve()}")

    if output_path is None:
        cache_dir = Path("data/cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        output = cache_dir / f"{source.stem}_16k.wav"
    else:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-ac",
        "1",
        "-ar",
        str(SAMPLE_RATE),
        "-af",
        "highpass=f=80,lowpass=f=7800,loudnorm=I=-18:LRA=11:TP=-1.5",
        str(output),
    ]

    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        raise RuntimeError("ffmpeg is not installed. Run: brew install ffmpeg")
    except subprocess.CalledProcessError:
        raise RuntimeError(f"ffmpeg failed to process audio: {source.resolve()}")

    return str(output)
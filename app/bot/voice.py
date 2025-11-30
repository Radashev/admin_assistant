# app/bot/voice.py
import json
import os
import subprocess
from pathlib import Path

from vosk import KaldiRecognizer, Model

# Можна перевизначити через змінну середовища FFMPEG_BIN, інакше просто "ffmpeg"
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")

VOSK_MODEL_PATH = Path("models/vosk-uk")

_model: Model | None = None


def get_model() -> Model:
    """Ліниве завантаження моделі (українська)."""
    global _model
    if _model is None:
        if not VOSK_MODEL_PATH.exists():
            raise RuntimeError(f"❗ Vosk модель не знайдена: {VOSK_MODEL_PATH}")
        _model = Model(str(VOSK_MODEL_PATH))
    return _model


async def voice_to_text(ogg_path: str) -> str:
    """
    Конвертуємо OGG -> WAV, розпізнаємо українську
    і повертаємо текст.
    """
    wav_path = ogg_path.replace(".ogg", ".wav")

    # Конвертація через ffmpeg
    subprocess.run(
        [FFMPEG_BIN, "-y", "-i", ogg_path, "-ar", "16000", "-ac", "1", wav_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    rec = KaldiRecognizer(get_model(), 16000)

    with open(wav_path, "rb") as f:
        while True:
            data = f.read(4000)
            if not data:
                break
            rec.AcceptWaveform(data)

    result = json.loads(rec.FinalResult())
    raw_text = result.get("text", "")

    if isinstance(raw_text, (list, tuple)):
        raw_text = " ".join(raw_text)
    if not isinstance(raw_text, str):
        raw_text = str(raw_text)

    text = raw_text.strip()
    print("VOSK DEBUG:", repr(text))  # дивишся в консолі, що він почув

    try:
        os.remove(ogg_path)
        os.remove(wav_path)
    except OSError:
        pass

    return text

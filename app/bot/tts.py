# app/bot/tts.py
import uuid
from pathlib import Path

from gtts import gTTS

TMP_DIR = Path("tmp")
TMP_DIR.mkdir(exist_ok=True)


def text_to_speech(text: str, lang: str = "en") -> Path:
    """
    Створює MP3 з тексту (TTS) і повертає шлях до файлу.
    lang:
      - 'en'  -> англійська
      - 'uk'  -> українська
      - 'pl'  -> польська
    """
    filename = TMP_DIR / f"tts_{lang}_{uuid.uuid4().hex}.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(str(filename))
    return filename

# app/bot/translator_multi.py
from deep_translator import GoogleTranslator

CYRILLIC_CHARS = set("абвгґдеєжзииіїйклмнопрстуфхцчшщьюяАБВГҐДЕЄЖЗИИІЙКЛМНОПРСТУФХЦЧШЩЬЮЯ")


def is_ukrainian(text: str) -> bool:
    """Якщо є хоч одна кирилична літера — вважаємо, що це українська."""
    return any(ch in CYRILLIC_CHARS for ch in text)


async def translate_ua_en(text: str) -> str:
    """
    Якщо текст українською → переклад у англійську.
    Якщо текст англійською → переклад в українську.
    Без польської, без langdetect, максимально просто.
    """
    text = text.strip()
    if not text:
        return "❗ Порожній текст для перекладу."

    if is_ukrainian(text):
        src = "uk"
        tgt = "en"
        direction = "🇺🇦 → 🇬🇧"
    else:
        src = "en"
        tgt = "uk"
        direction = "🇬🇧 → 🇺🇦"

    translated = GoogleTranslator(source=src, target=tgt).translate(text)

    return (
        f"{direction}\n\n" f"📝 Оригінал:\n<b>{text}</b>\n\n" f"🔁 Переклад:\n<b>{translated}</b>"
    )

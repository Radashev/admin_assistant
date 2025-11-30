# app/bot/handlers.py
import os
from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from sqlalchemy import text

from app.bot.gcal import add_event_to_gcal
from app.bot.scheduler import schedule_reminder
from app.bot.tasks import add_task_to_db, get_tasks_from_db
from app.bot.translator_multi import translate_ua_en
from app.bot.voice import voice_to_text
from app.db.mongo import get_mongo_db
from app.db.postgres import AsyncSessionLocal

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    /start – перший контакт бота з користувачем:
    - лог у Mongo
    - простий тест підключення до Postgres
    """
    user = message.from_user

    # ---------- Mongo: лог команди ----------
    mongo_db = get_mongo_db()
    await mongo_db.telegram_logs.insert_one(
        {
            "telegram_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "command": "/start",
            "timestamp": datetime.utcnow(),
        }
    )

    # ---------- Postgres: простий SELECT 1 ----------
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        db_ok = result.scalar_one_or_none()

    await message.answer(
        "Привіт! Я твій бот admin_assistant 🤖\n"
        f"Mongo логування: ✅\n"
        f"Postgres підключення: {'✅' if db_ok == 1 else '⚠️ є проблема'}"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """
    /help – українська довідка
    """
    text = (
        "ℹ️ <b>Довідка по командам admin_assistant 🤖</b>\n\n"
        "👋 <b>/start</b>\n"
        "   Перший запуск бота, перевірка підключення до Mongo та Postgres.\n\n"
        "❓ <b>/help</b>\n"
        "   Ця довідка з описом команд.\n\n"
        "❓ <b>/help_en</b>\n"
        "   English version of help.\n\n"
        "🧑 <b>/whoami</b>\n"
        "   Показує твої дані з Telegram (ID, username, ім’я).\n\n"
        "🏓 <b>/ping</b>\n"
        "   Перевірка підключення до Mongo та Postgres.\n\n"
        "🗃 <b>/add_task &lt;текст&gt;</b>\n"
        "   Додати задачу/нотатку у базу.\n"
        "   Приклад: <code>/add_task Подзвонити рекрутеру</code>\n\n"
        "📋 <b>/tasks</b>\n"
        "   Показати список збережених задач.\n\n"
        "🌍 <b>/tr &lt;текст&gt;</b>\n"
        "   Переклад українська ↔ англійська.\n"
        "   Приклади:\n"
        "   <code>/tr Я шукаю роботу DevOps інженером</code>\n"
        "   <code>/tr I am looking for a DevOps job</code>\n\n"
        "⏰ <b>/remind YYYY-MM-DD HH:MM текст</b>\n"
        "   Створити локальне нагадування через бот.\n"
        "   Приклад: <code>/remind 2025-11-27 14:30 Вийти з дому</code>\n\n"
        "📅 <b>/gcal YYYY-MM-DD HH:MM текст</b>\n"
        "   Додати подію в Google Calendar.\n"
        "   Приклад: <code>/gcal 2025-11-27 14:30 Зустріч з рекрутером</code>\n\n"
        "💬 <b>Авто-переклад тексту</b>\n"
        "   Якщо ти просто пишеш повідомлення без /команди, бот автоматично\n"
        "   перекладає текст українська ↔ англійська.\n\n"
        "🎙 <b>Голосовий режим</b>\n"
        "   Надішли голосове повідомлення українською  – я розпізнаю текст\n"
        "   і перекладу його  англійською.\n\n"
        "⚠️ <b>Розширені голосові команди</b>\n"
        '   (типу "запиши", "переклади", "зроби нотатку", "нагадай") ще НЕ\n'
        "   реалізовані та знаходяться в розробці.\n\n"
        "🌐 <i>English version:</i> <b>/help_en</b>\n"
    )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("help_en"))
async def cmd_help_en(message: Message):
    """
    /help_en – English help
    """
    text = (
        "ℹ️ <b>Admin Assistant Bot – Help Menu 🤖</b>\n\n"
        "👋 <b>/start</b>\n"
        "   Initializes the bot and checks Mongo & Postgres connections.\n\n"
        "❓ <b>/help_en</b>\n"
        "   This help menu.\n\n"
        "❓ <b>/help</b>\n"
        "   Україномовна версія довідки.\n\n"
        "🧑 <b>/whoami</b>\n"
        "   Shows your Telegram ID, username, first & last name.\n\n"
        "🏓 <b>/ping</b>\n"
        "   Tests Mongo and Postgres connectivity.\n\n"
        "🗃 <b>/add_task &lt;text&gt;</b>\n"
        "   Adds a task/note to the database.\n"
        "   Example: <code>/add_task Call the recruiter</code>\n\n"
        "📋 <b>/tasks</b>\n"
        "   Displays the list of your saved tasks.\n\n"
        "🌍 <b>/tr &lt;text&gt;</b>\n"
        "   Translates English ↔ Ukrainian automatically.\n"
        "   Examples:\n"
        "   <code>/tr I am looking for a DevOps job</code>\n"
        "   <code>/tr Я шукаю роботу DevOps інженером</code>\n\n"
        "⏰ <b>/remind YYYY-MM-DD HH:MM text</b>\n"
        "   Creates a bot-side reminder.\n"
        "   Example: <code>/remind 2025-11-27 14:30 Leave home</code>\n\n"
        "📅 <b>/gcal YYYY-MM-DD HH:MM text</b>\n"
        "   Adds an event to Google Calendar.\n"
        "   Example: <code>/gcal 2025-11-27 14:30 Meeting with recruiter</code>\n\n"
        "💬 <b>Auto-translation</b>\n"
        "   If you send plain text (without a slash command), the bot\n"
        "   automatically translates English ↔ Ukrainian.\n\n"
        "🎙 <b>Voice mode</b>\n"
        "   Send a voice message in Ukrainian  – I will recognize the text\n"
        "   and translate it English .\n\n"
        "⚠️ <b>Advanced voice commands</b>\n"
        '   (such as "запиши", "переклади", "зроби нотатку", "нагадай") are NOT\n'
        "   implemented yet and currently in development.\n\n"
        "🌐 <i>Українська версія:</i> <b>/help</b>\n"
    )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("dbtest"))
async def cmd_dbtest(message: Message):
    """
    /dbtest – окремий тест Postgres (можна переробити під реальну бізнес-логіку)
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        value = result.scalar_one_or_none()

    await message.answer(f"Результат SELECT 1 з Postgres: <b>{value}</b>")


@router.message(Command("whoami"))
async def cmd_whoami(message: Message):
    """
    /whoami – показує basic інфу про користувача.
    Потім можемо прив’язати до таблиці users в Postgres.
    """
    user = message.from_user
    await message.answer(
        "Твої дані з Telegram:\n"
        f"ID: <code>{user.id}</code>\n"
        f"Username: @{user.username}\n"
        f"First name: {user.first_name}\n"
        f"Last name: {user.last_name}"
    )


@router.message(Command("ping"))
async def cmd_ping(message: Message):
    """
    /ping — перевірка підключення до Mongo та Postgres
    """
    user = message.from_user

    # --- Mongo ---
    mongo_db = get_mongo_db()
    await mongo_db.telegram_logs.insert_one(
        {
            "telegram_id": user.id,
            "username": user.username,
            "command": "/ping",
            "ts": datetime.utcnow(),
        }
    )

    # --- Postgres ---
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        pg_ok = result.scalar_one_or_none()

    await message.answer(
        "Pong! 🏓\n" f"Mongo: <b>OK</b> ✅\n" f"Postgres: <b>{'OK' if pg_ok == 1 else 'ERROR'}</b>"
    )


@router.message(Command("add_task"))
async def add_task(message: types.Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("❗ Введи текст задачі.\nПриклад: /add_task Купити молоко")
        return

    task_text = args[1]

    inserted_id = await add_task_to_db(message.from_user.id, task_text)

    await message.answer(f"🟢 Завдання додано!\nID: `{inserted_id}`", parse_mode="Markdown")


@router.message(Command("tasks"))
async def show_tasks(message: types.Message):
    telegram_id = message.from_user.id
    tasks = await get_tasks_from_db(telegram_id)

    if not tasks:
        await message.answer("📭 У тебе поки що немає задач.")
        return

    lines = ["📝 Твої задачі:"]
    for i, task in enumerate(tasks, start=1):
        lines.append(f"{i}. {task['text']}")

    await message.answer("\n".join(lines))


@router.message(Command("tr"))
async def translate_to_en_ua(message: types.Message):
    """
    /tr <текст> — українська ↔ англійська.
    Якщо текст українською – переклад в англійську.
    Якщо текст англійською – переклад в українську.
    """
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            "Введи текст для перекладу:\n"
            "/tr Я шукаю роботу DevOps інженером\n"
            "/tr I am looking for a DevOps job"
        )
        return

    text = args[1].strip()
    if not text:
        await message.answer("Текст для перекладу порожній 🙃")
        return

    result = await translate_ua_en(text)
    await message.answer(result, parse_mode="HTML")


@router.message(F.text.regexp(r"^[^/].*"))
async def auto_translate_plain_text(message: types.Message):
    """
    Авто-переклад будь-якого тексту (НЕ команда).
    UA ↔ EN.
    """
    text = message.text.strip()
    if not text:
        return

    result = await translate_ua_en(text)
    await message.answer(result, parse_mode="HTML")


@router.message(F.voice)
async def handle_voice(message: types.Message, bot: Bot):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)

    os.makedirs("tmp", exist_ok=True)
    ogg_path = f"tmp/{file_id}.ogg"

    await bot.download_file(file.file_path, destination=ogg_path)

    try:
        text = await voice_to_text(ogg_path)
    except Exception as e:
        print("VOICE ERROR:", repr(e))
        await message.answer("❗ Не зміг розпізнати голос. Спробуй ще раз.")
        return

    if not text:
        await message.answer("🤷 Голос тихий або нерозбірливий. Спробуй чіткіше.")
        return

    original_text = text.strip()

    # показуємо, що почув
    await message.answer(
        f"🎙️ Я почув (UA/EN):\n<b>{original_text}</b>",
        parse_mode="HTML",
    )

    # перекладаємо тим самим ядром, що і текст
    result = await translate_ua_en(original_text)
    await message.answer(result, parse_mode="HTML")


@router.message(Command("remind"))
async def remind(message: types.Message, bot: Bot):
    """
    Приклад:
    /remind 2025-11-26 14:30 Вийти з дому
    """

    try:
        _, date_str, time_str, *text_list = message.text.split()
        text = " ".join(text_list)
        run_date = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
    except Exception:
        await message.answer(
            "❗ Формат неправильний.\n" "Приклад:\n" "/remind 2025-11-26 14:30 Вийти з дому"
        )
        return

    schedule_reminder(
        bot=bot,
        chat_id=message.chat.id,
        text=text,
        run_date=run_date,
    )

    await message.answer(f"⏳ Нагадування створено!\n📅 {run_date}\n📝 {text}")


@router.message(Command("gcal"))
async def add_to_google_calendar(message: types.Message):
    """
    /gcal 2025-11-27 14:30 Зустріч на ярмарку вакансій
    """

    try:
        _, date_str, time_str, *event_text = message.text.split()
        summary = " ".join(event_text)
        dt = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
    except Exception:
        await message.answer(
            "❗ Формат неправильний\n" "Приклад:\n" "/gcal 2025-11-27 14:30 Зустріч з рекрутером"
        )
        return

    link = add_event_to_gcal(summary, dt)

    await message.answer(
        f"📅 Подію додано в Google Calendar!\n\n"
        f"📝 <b>{summary}</b>\n"
        f"⏰ {dt}\n\n"
        f"🔗 <a href='{link}'>Відкрити в календарі</a>",
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


def register_handlers(dp):
    """
    Викликається з main_bot.py, щоб підключити router.
    """
    dp.include_router(router)

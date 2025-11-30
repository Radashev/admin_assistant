from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


async def send_reminder(bot: Bot, chat_id: int, text: str):
    await bot.send_message(chat_id, f"⏰ Нагадування:\n<b>{text}</b>", parse_mode="HTML")


def schedule_reminder(bot: Bot, chat_id: int, text: str, run_date):
    scheduler.add_job(send_reminder, "date", run_date=run_date, args=[bot, chat_id, text])

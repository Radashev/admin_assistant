import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.handlers import register_handlers
from app.bot.scheduler import scheduler
from app.core.config import settings


async def main():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    register_handlers(dp)

    scheduler.start()

    print("Telegram bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

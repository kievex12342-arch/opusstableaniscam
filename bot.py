import asyncio
import logging
import os
import shutil
from logging.handlers import RotatingFileHandler


from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import start, check, admin, add_scammer, subscription, keys
from keep_alive import keep_alive

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler("logs/bot.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

keep_alive()


def create_backup():
    try:
        os.makedirs("backups", exist_ok=True)
        db_path = os.path.join("data", "database.db")
        if os.path.exists(db_path):
            shutil.copy2(db_path, os.path.join("backups", "database_backup.db"))
            logger.info("Database backup created")
    except Exception as e:
        logger.error(f"Backup error: {e}")


async def main():
    import database as db
    db.init_db()
    db.cleanup_old_cache()
    create_backup()

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(admin.router)
    dp.include_router(keys.router)
    dp.include_router(add_scammer.router)
    dp.include_router(start.router)
    dp.include_router(subscription.router)
    dp.include_router(check.router)

    logger.info("🛡 OpusGuru Anti-Scam Bot запущен!")
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logger.exception(f"Polling crashed: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())



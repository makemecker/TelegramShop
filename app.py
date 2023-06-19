import os
import handlers
from data import config
from loader import dp, db, bot
import logging
import asyncio


WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 5000))
user_message = 'Пользователь'
admin_message = 'Админ'


async def on_startup():
    logging.basicConfig(level=logging.INFO)
    db.create_tables()

    await bot.delete_webhook()
    await bot.set_webhook(config.WEBHOOK_URL)


async def on_shutdown():
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bot down")


async def main() -> None:
    await dp.start_polling(bot, on_startup=on_startup, skip_updates=False)

if __name__ == '__main__':
    # Запуск бота
    asyncio.run(main())


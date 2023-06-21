import logging
import asyncio
from config import Config, load_config
from aiogram import Bot, Dispatcher
from handlers import router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode


async def main() -> None:
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dp: Dispatcher = Dispatcher(admins=config.tg_bot.admins, storage=storage, threshold=config.delivery_threshold,
                                database=config.database)

    # Регистрируем роутеры в диспетчере
    dp.include_router(router)

    config.database.create_tables()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.ERROR,  # Уровень логирования (в данном случае, только ошибки)
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат записи логов
        filename='bot.log',  # Имя файла логов
    )
    # Запуск бота
    asyncio.run(main())

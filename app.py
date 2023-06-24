import logging
import asyncio
from config import Config, load_config
from aiogram import Bot, Dispatcher
from handlers import router
from aiogram.fsm.storage.memory import MemoryStorage
from keyboards.main_menu import set_main_menu

# Инициализируем логгер
logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,  # Уровень логирования
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат записи логов
        filename='bot.log',  # Имя файла логов
        filemode='w'  # Затирание файла с новым запуском
    )
    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    storage = MemoryStorage()
    dp: Dispatcher = Dispatcher(admins=config.tg_bot.admins, storage=storage, threshold=config.delivery_threshold,
                                database=config.database)

    # Настраиваем главное меню бота
    await set_main_menu(bot)

    # Регистрируем роутеры в диспетчере
    dp.include_router(router)

    config.database.create_tables()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    # Запуск бота
    asyncio.run(main())

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from utils.db.storage import DatabaseManager
from aiogram.enums.parse_mode import ParseMode
from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
db = DatabaseManager('data/database.db')

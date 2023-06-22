from aiogram import F
from aiogram.types import CallbackQuery
from aiogram import Router
from database.storage import DatabaseManager
from lexicon import LEXICON
from handlers.handler_functions import delivery_status_answer

# Инициализируем роутер уровня модуля
delivery_router: Router = Router()


@delivery_router.callback_query(F.data == 'status')
async def process_delivery_status(callback: CallbackQuery, database: DatabaseManager):
    message = callback.message
    orders = database.fetchall('SELECT * FROM orders WHERE cid=?', (message.chat.id,))
    
    if len(orders) == 0:
        await message.answer(LEXICON['status_no'])
    else:
        await delivery_status_answer(message, orders)
    await callback.answer()

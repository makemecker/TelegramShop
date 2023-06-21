from aiogram import F
from aiogram.types import CallbackQuery
from aiogram import Router
from database.storage import DatabaseManager

# Инициализируем роутер уровня модуля
delivery_router: Router = Router()


@delivery_router.callback_query(F.data == 'status')
async def process_delivery_status(callback: CallbackQuery, database: DatabaseManager):
    message = callback.message
    orders = database.fetchall('SELECT * FROM orders WHERE cid=?', (message.chat.id,))
    
    if len(orders) == 0:
        await message.answer('У вас нет активных заказов.')
    else:
        await delivery_status_answer(message, orders)
    await callback.answer()


async def delivery_status_answer(message, orders):

    res = ''

    for order in orders:

        res += f'Заказ <b>№{order[3]}</b>'
        answer = [
            ' лежит на складе.',
            ' уже в пути!',
            ' прибыл и ждет вас на почте!'
        ]

        res += answer[0]
        res += '\n\n'

    await message.answer(res)

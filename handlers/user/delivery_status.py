
from aiogram.types import Message
from loader import dp, db
from .menu import delivery_status
from filters import IsUser
from aiogram import F
from aiogram.types import CallbackQuery


@dp.callback_query(F.data == 'status')
async def process_delivery_status(callback: CallbackQuery):
    message = callback.message
    orders = db.fetchall('SELECT * FROM orders WHERE cid=?', (message.chat.id,))
    
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

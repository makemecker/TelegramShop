
from aiogram.types import Message
from loader import dp, db
from handlers.user.menu import orders_kb
from filters import IsAdmin
from aiogram import F


@dp.message(IsAdmin(), F.text == orders_kb.text)
async def process_orders(message: Message):
    
    orders = db.fetchall('SELECT * FROM orders')
    
    if len(orders) == 0:
        await message.answer('У вас нет заказов.')
    else:
        await order_answer(message, orders)


async def order_answer(message, orders):

    res = ''

    for order in orders:
        res += f'Заказ <b>№{order[3]}</b>\n\n'

    await message.answer(res)

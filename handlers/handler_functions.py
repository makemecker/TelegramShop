from keyboards.kb_generator import create_inline_kb
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from aiogram.types import Message, BufferedInputFile
from aiogram.enums.chat_action import ChatAction
from keyboards.products_from_catalog import product_markup
from lexicon import LEXICON


async def checkout(state: FSMContext, threshold: int, admins: list, bot: Bot, message=None, info_to_admin=False):
    answer = ''
    total_price = 0

    for title, price, count_in_cart in (await state.get_data())['products'].values():
        if count_in_cart > 0:
            tp = count_in_cart * price
            answer += f'<b>{title}</b> * {count_in_cart}шт. = {tp}₽\n'
            total_price += tp

    delivery = ''
    if total_price < threshold:
        delivery = LEXICON['threshold_to_admin'].format(threshold) if info_to_admin \
            else LEXICON['threshold_to_user'].format(threshold)
    if info_to_admin:
        for admin_id in admins:
            await bot.send_message(admin_id, LEXICON['order_info'].format(answer, total_price, delivery))
    else:
        markup = create_inline_kb('all_right', 'back')
        await message.answer(LEXICON['order_info'].format(answer, total_price, delivery),
                             reply_markup=markup)


async def confirm(message: Message):
    markup = create_inline_kb('confirm', 'back')
    await message.answer(LEXICON['check'],
                         reply_markup=markup)


async def show_products(message: Message, products: list, bot: Bot):
    if len(products) == 0:

        await message.answer(LEXICON['nothing'])

    else:

        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        for idx, title, body, image, price, _ in products:
            markup = product_markup(idx, price)
            text = f'<b>{title}</b>\n\n{body}'
            if image is not None:
                await message.answer_photo(photo=BufferedInputFile(image, filename=text),
                                           caption=text,
                                           reply_markup=markup)
            else:
                await message.answer(text=title, reply_markup=markup)
        transition_markup = create_inline_kb('catalog', 'cart')
        await message.answer(text=LEXICON['submenu'],
                             reply_markup=transition_markup)


async def delivery_status_answer(message: Message, orders: list):
    res = ''

    for order in orders:
        res += f'Заказ <b>№{order[3]}</b>'
        answer = [
            LEXICON['status_warehouse'],
            LEXICON['status_on_way'],
            LEXICON['status_delivered']
        ]

        res += answer[0]
        res += '\n\n'

    await message.answer(res)

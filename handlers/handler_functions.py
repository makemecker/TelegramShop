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


async def show_products(message: Message, products: list, bot: Bot, state: FSMContext):
    if len(products) == 0:

        await message.answer(LEXICON['nothing'])

    else:

        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        len_products = len(products)
        show_len = 10

        data = await state.get_data()

        start_index = 0 if "start_index" not in data.keys() else data["start_index"]
        end_index = start_index + show_len if start_index + show_len <= len_products else len_products

        for idx, title, body, image, price, _ in products[start_index:end_index]:
            markup = product_markup(idx, price)
            text = f'<b>{title}</b>\n\n{body}'
            if image is not None:
                await message.answer_photo(photo=BufferedInputFile(image, filename=text),
                                           caption=text,
                                           reply_markup=markup)
            else:
                await message.answer(text=title, reply_markup=markup)

        if start_index == 0:
            if end_index != len_products:
                await state.update_data(start_index=end_index)
                # await message c кнопкой только вперед
                transition_markup = create_inline_kb('pagination_forward', 'catalog', 'cart')
                await message.answer(text=LEXICON['submenu'],
                                     reply_markup=transition_markup)
            else:
                transition_markup = create_inline_kb('catalog', 'cart')
                await message.answer(text=LEXICON['submenu'],
                                     reply_markup=transition_markup)
                # await message без пагинаций
        else:
            if end_index != len_products:
                transition_markup = create_inline_kb('pagination_forward', 'pagination_back', 'catalog', 'cart')
                await state.update_data(start_index=end_index)
                await message.answer(text=LEXICON['submenu'],
                                     reply_markup=transition_markup)
                # await message c кнопкой вперед и назад
            else:
                transition_markup = create_inline_kb('pagination_back', 'catalog', 'cart')
                await state.update_data(start_index=end_index)
                await message.answer(text=LEXICON['submenu'],
                                     reply_markup=transition_markup)
                # await message c кнопкой назад


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

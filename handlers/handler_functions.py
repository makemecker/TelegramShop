from keyboards.kb_generator import create_inline_kb
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from aiogram.types import Message, BufferedInputFile
from aiogram.enums.chat_action import ChatAction
from keyboards.products_from_catalog import product_markup


async def checkout(state: FSMContext, threshold: int, admins: list, bot: Bot, message=None, info_to_admin=False):
    answer = ''
    total_price = 0

    data = await state.get_data()
    for title, price, count_in_cart in data['products'].values():
        tp = count_in_cart * price
        answer += f'<b>{title}</b> * {count_in_cart}шт. = {tp}₽\n'
        total_price += tp

    delivery = ''
    if total_price < threshold:
        delivery = f'\n\n Сумма заказа составляет менее {threshold}₽, поэтому доставка заказа платная. ' + \
                   ('Надо определить стоимость доставки до клиента' if info_to_admin
                    else 'Стоимость доставки Менеджер сообщит дополнительно.')
    if info_to_admin:
        for admin_id in admins:
            await bot.send_message(admin_id,
                                   f'{answer}\nОбщая сумма заказа: {total_price}₽. {delivery}')
    else:
        markup = create_inline_kb('all_right', 'back')
        await message.answer(f'{answer}\nОбщая сумма заказа: {total_price}₽. {delivery}',
                             reply_markup=markup)


async def confirm(message: Message):
    markup = create_inline_kb('confirm', 'back')
    await message.answer('Убедитесь, что все правильно оформлено и подтвердите заказ.',
                         reply_markup=markup)


async def show_products(message: Message, products: list, bot: Bot):
    if len(products) == 0:

        await message.answer('Здесь ничего нет 😢')

    else:

        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        for idx, title, body, image, price, _ in products:
            markup = product_markup(idx, price)
            text = f'<b>{title}</b>\n\n{body}'

            await message.answer_photo(photo=BufferedInputFile(image, filename=text),
                                       caption=text,
                                       reply_markup=markup)
        transition_markup = create_inline_kb('menu', 'catalog', 'cart')
        await message.answer(text='Что вы хотите сделать?',
                             reply_markup=transition_markup)

import logging
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, BufferedInputFile
from keyboards.inline.products_from_cart import product_markup, ProductCb
from keyboards.default.markups import *
from aiogram.enums.chat_action import ChatAction
from states import CheckoutState
from loader import dp, db, bot
from filters import IsUser
from .menu import cart
from data.config import THRESHOLD, ADMINS
from aiogram.filters import StateFilter
from aiogram import F


@dp.message(IsUser(), F.text == cart.text)
@dp.message(IsUser(), F.text == cart_message.text)
async def process_cart(message: Message, state: FSMContext):
    cart_data = db.fetchall(
        'SELECT * FROM cart WHERE cid=?', (message.chat.id,))

    if len(cart_data) == 0:

        await message.answer('Ваша корзина пуста.')

    else:

        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        data = await state.get_data()
        data['products'] = {}

        order_cost = 0

        for _, idx, count_in_cart in cart_data:

            product = db.fetchone('SELECT * FROM products WHERE idx=?', (idx,))

            if product is None:

                db.query('DELETE FROM cart WHERE idx=?', (idx,))

            else:
                _, title, body, image, price, _ = product
                order_cost += price

                data['products'][idx] = [title, price, count_in_cart]

                markup = product_markup(idx, count_in_cart)
                text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price}₽.'

                await message.answer_photo(photo=BufferedInputFile(image, filename=text),
                                           caption=text,
                                           reply_markup=markup)
        await state.set_data(data=data)
        if order_cost != 0:
            markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='📦 Оформить заказ')]], resize_keyboard=True,
                                         selective=True)
            await message.answer('Перейти к оформлению?',
                                 reply_markup=markup)


@dp.callback_query(IsUser(), ProductCb.filter(F.action == 'count'))
@dp.callback_query(IsUser(), ProductCb.filter(F.action == 'increase'))
@dp.callback_query(IsUser(), ProductCb.filter(F.action == 'decrease'))
@dp.callback_query(IsUser(), ProductCb.filter(F.action == 'increase10'))
@dp.callback_query(IsUser(), ProductCb.filter(F.action == 'decrease10'))
@dp.callback_query(IsUser(), ProductCb.filter(F.action == 'count50'))
@dp.callback_query(IsUser(), ProductCb.filter(F.action == 'count100'))
@dp.callback_query(IsUser(), ProductCb.filter(F.action == 'reset'))
async def product_callback_handler(query: CallbackQuery, callback_data: ProductCb, state: FSMContext):
    idx = callback_data.id
    action = callback_data.action
    data = await state.get_data()
    if 'count' == action:
        if 'products' not in data.keys():

            await process_cart(query.message, state)

        else:

            await query.answer('Количество - ' + data['products'][idx][2])

    else:
        if 'products' not in data.keys():

            await process_cart(query.message, state)

        else:
            change_reactions = {
                'increase': 1,
                'decrease': -1,
                'increase10': 10,
                'decrease10': -10,
            }
            assign_reactions = {
                'count50': 50,
                'count100': 100,
                'reset': 0
            }
            if change_reactions.get(action):
                data['products'][idx][2] += change_reactions[action]
            else:
                data['products'][idx][2] = assign_reactions[action]
            count_in_cart = data['products'][idx][2]
            await state.set_data(data)
            if count_in_cart <= 0:
                count_in_cart = 0
                db.query('''DELETE FROM cart
                    WHERE cid = ? AND idx = ?''', (query.message.chat.id, idx))

                await query.message.delete()
            else:

                db.query('''UPDATE cart 
                    SET quantity = ? 
                    WHERE cid = ? AND idx = ?''', (count_in_cart, query.message.chat.id, idx))

                await query.message.edit_reply_markup(reply_markup=product_markup(idx, count_in_cart))


@dp.message(IsUser(), F.text == '📦 Оформить заказ')
async def process_checkout(message: Message, state: FSMContext):
    await state.set_state(CheckoutState.check_cart)
    await checkout(message=message, state=state)


async def checkout(state, message=None, info_to_admin=False):
    answer = ''
    total_price = 0

    data = await state.get_data()
    for title, price, count_in_cart in data['products'].values():
        tp = count_in_cart * price
        answer += f'<b>{title}</b> * {count_in_cart}шт. = {tp}₽\n'
        total_price += tp

    delivery = ''
    if total_price < THRESHOLD:
        delivery = f'\n\n Сумма заказа составляет менее {THRESHOLD}₽, поэтому доставка заказа платная. ' + \
                   ('Надо определить стоимость доставки до клиента' if info_to_admin
                    else 'Стоимость доставки Менеджер сообщит дополнительно.')
    if info_to_admin:
        for admin_id in ADMINS:
            await bot.send_message(admin_id,
                                   f'{answer}\nОбщая сумма заказа: {total_price}₽. {delivery}')
    else:
        await message.answer(f'{answer}\nОбщая сумма заказа: {total_price}₽. {delivery}',
                             reply_markup=check_markup())


@dp.message(IsUser(), lambda message: message.text not in [all_right_message.text, back_message.text],
            StateFilter(CheckoutState.check_cart))
async def process_check_cart_invalid(message: Message):
    await message.reply('Такого варианта не было.')


@dp.message(IsUser(), F.text == back_message.text, StateFilter(CheckoutState.check_cart))
async def process_check_cart_back(message: Message, state: FSMContext):
    await state.clear()
    await process_cart(message, state)


@dp.message(IsUser(), F.text == all_right_message.text, StateFilter(CheckoutState.check_cart))
async def process_check_cart_all_right(message: Message, state: FSMContext):
    await state.set_state(CheckoutState.name)
    await message.answer('Укажите, пожалуйста, Ваше имя',
                         reply_markup=back_markup())


@dp.message(IsUser(), F.text == back_message.text, StateFilter(CheckoutState.name))
async def process_name_back(message: Message, state: FSMContext):
    await state.set_state(CheckoutState.check_cart)
    await checkout(message=message, state=state)


@dp.message(IsUser(), StateFilter(CheckoutState.name))
async def process_name(message: Message, state: FSMContext):
    data = await state.get_data()
    data['name'] = message.text
    await state.set_data(data)
    if 'address' in data.keys():

        await confirm(message)
        await state.set_state(CheckoutState.confirm)

    else:
        await state.set_state(CheckoutState.address)
        await message.answer('Укажите, пожалуйста, адрес доставки',
                             reply_markup=back_markup())


@dp.message(IsUser(), F.text == back_message.text, StateFilter(CheckoutState.address))
async def process_address_back(message: Message, state: FSMContext):
    await message.answer('Изменить имя с <b>' + (await state.get_data())['name'] + '</b>?',
                         reply_markup=back_markup())
    await state.set_state(CheckoutState.name)


@dp.message(IsUser(), StateFilter(CheckoutState.address))
async def process_address(message: Message, state: FSMContext):
    data = await state.get_data()
    data['address'] = message.text
    await state.set_data(data)
    await state.set_state(CheckoutState.phone)
    await message.answer('Укажите, пожалуйста, телефон для связи',
                         reply_markup=back_markup())


@dp.message(IsUser(), F.text == back_message.text, StateFilter(CheckoutState.phone))
async def process_address_back(message: Message, state: FSMContext):
    await message.answer('Изменить адрес: <b>' + (await state.get_data())['address'] + '</b>?',
                         reply_markup=back_markup())
    await state.set_state(CheckoutState.address)


@dp.message(IsUser(), StateFilter(CheckoutState.phone))
async def process_address(message: Message, state: FSMContext):
    data = await state.get_data()
    data['phone'] = message.text
    await state.set_data(data)

    await confirm(message)
    await state.set_state(CheckoutState.confirm)


async def confirm(message):
    await message.answer('Убедитесь, что все правильно оформлено и подтвердите заказ.',
                         reply_markup=confirm_markup())


@dp.message(IsUser(), lambda message: message.text not in [confirm_message.text, back_message.text],
            StateFilter(CheckoutState.confirm))
async def process_confirm_invalid(message: Message):
    await message.reply('Такого варианта не было.')


@dp.message(IsUser(), F.text == back_message.text, StateFilter(CheckoutState.confirm))
async def process_confirm(message: Message, state: FSMContext):
    await state.set_state(CheckoutState.phone)
    await message.answer('Изменить телефон: <b>' + (await state.get_data())['phone'] + '</b>?',
                         reply_markup=back_markup())


@dp.message(IsUser(), F.text == confirm_message.text, StateFilter(CheckoutState.confirm))
async def process_confirm(message: Message, state: FSMContext):
    enough_money = True  # enough money on the balance sheet
    markup = ReplyKeyboardRemove()

    if enough_money:

        logging.info('Deal was made.')
        data = await state.get_data()
        cid = message.chat.id
        products = [idx + '=' + str(quantity)
                    for idx, quantity in db.fetchall('''SELECT idx, quantity FROM cart
        WHERE cid=?''', (cid,))]  # idx=quantity

        db.query('INSERT INTO orders VALUES (?, ?, ?, ?)',
                 (cid, data['name'], data['address'], ' '.join(products)))

        db.query('DELETE FROM cart WHERE cid=?', (cid,))

        await message.answer('Отлично! Наш Менеджер свяжется с Вами в ближайшее время 🚀\n'
                             'Имя: <b>' + data['name'] + '</b>' +
                             '\nАдрес: <b>' + data['address'] + '</b>' +
                             '\nТелефон: <b>' + data['phone'] + '</b>',

                             reply_markup=markup)
        for admin_id in ADMINS:
            await bot.send_message(admin_id,
                                   "Оформлен новый заказ!\n"
                                   f"Пользователь: @{message.from_user.username}\n"
                                   f"User_id: {message.from_user.id}\n"
                                   'Имя: <b>' + data['name'] + '</b>' +
                                   '\nАдрес: <b>' + data['address'] + '</b>' +
                                   '\nТелефон: <b>' + data['phone'] + '</b>\n'
                                   )
        await checkout(state=state, info_to_admin=True)
    else:

        await message.answer('У вас недостаточно денег на счете. Пополните баланс!',
                             reply_markup=markup)

    await state.clear()

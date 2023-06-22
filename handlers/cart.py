import logging
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, BufferedInputFile
from keyboards.products_from_cart import product_markup, ProductCb
from aiogram.enums.chat_action import ChatAction
from states import CheckoutState
from aiogram.filters import StateFilter
from aiogram import F
from keyboards.kb_generator import create_inline_kb
from aiogram import Router, Bot
from database.storage import DatabaseManager
from handlers.handler_functions import checkout, confirm
from lexicon import LEXICON

# Инициализируем роутер уровня модуля
cart_router: Router = Router()


@cart_router.callback_query(F.data == 'cart')
async def process_cart(callback: CallbackQuery, state: FSMContext, database: DatabaseManager, bot: Bot):
    message = callback.message
    cart_data = database.fetchall('SELECT * FROM cart WHERE cid=?', (message.chat.id,))
    if len(cart_data) == 0:
        await message.answer(LEXICON['empty_cart'])
        await callback.answer()
    else:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        data = await state.get_data()
        data['products'] = {}
        order_cost = 0
        for _, idx, count_in_cart in cart_data:

            product = database.fetchone('SELECT * FROM products WHERE idx=?', (idx,))

            if product is None:

                database.query('DELETE FROM cart WHERE idx=?', (idx,))

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
            markup = create_inline_kb('order', 'menu')
            await message.answer(LEXICON['to_registration'], reply_markup=markup)
        await callback.answer()


@cart_router.callback_query(ProductCb.filter(F.action.in_({'increase', 'decrease', 'increase10', 'decrease10',
                                                           'count50', 'count100', 'reset'})))
async def product_callback_handler(callback: CallbackQuery, callback_data: ProductCb, state: FSMContext,
                                   database: DatabaseManager):
    idx = callback_data.id
    action = callback_data.action
    data = await state.get_data()
    if 'count' == action:
        if 'products' not in data.keys():

            await process_cart(callback, state)

        else:

            await callback.message.answer(LEXICON['count'].format(data['products'][idx][2]))

    else:
        if 'products' not in data.keys():

            await process_cart(callback, state)

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
                if data['products'][idx][2] < 0:
                    data['products'][idx][2] = 0
            else:
                data['products'][idx][2] = assign_reactions[action]
            count_in_cart = data['products'][idx][2]
            await state.set_data(data)
            if count_in_cart <= 0:
                database.query('''DELETE FROM cart
                    WHERE cid = ? AND idx = ?''', (callback.message.chat.id, idx))

                await callback.message.delete()
            else:

                database.query('''UPDATE cart 
                    SET quantity = ? 
                    WHERE cid = ? AND idx = ?''', (count_in_cart, callback.message.chat.id, idx))

                await callback.message.edit_reply_markup(reply_markup=product_markup(idx, count_in_cart))


@cart_router.callback_query(F.data == 'order')
async def process_checkout(callback: CallbackQuery, state: FSMContext, threshold: int, admins: list, bot: Bot):
    await state.set_state(CheckoutState.check_cart)
    await checkout(message=callback.message, state=state, threshold=threshold, admins=admins, bot=bot)
    await callback.answer()


@cart_router.callback_query(F.data == 'back', StateFilter(CheckoutState.check_cart))
async def process_check_cart_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await process_cart(callback, state)
    await callback.answer()


@cart_router.callback_query(F.data == 'all_right', StateFilter(CheckoutState.check_cart))
async def process_check_cart_all_right(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutState.name)
    markup = create_inline_kb('back')
    await callback.message.answer(LEXICON['set_name'], reply_markup=markup)
    await callback.answer()


@cart_router.callback_query(F.data == 'back', StateFilter(CheckoutState.name))
async def process_name_back(callback: CallbackQuery, state: FSMContext, threshold: int, admins: list,
                            bot: Bot):
    await state.set_state(CheckoutState.check_cart)
    await checkout(message=callback.message, state=state, threshold=threshold, admins=admins, bot=bot)
    await callback.answer()


@cart_router.message(StateFilter(CheckoutState.name))
async def process_name(message: Message, state: FSMContext):
    data = await state.get_data()
    data['name'] = message.text
    await state.set_data(data)
    if 'address' in data.keys():
        await confirm(message)
        await state.set_state(CheckoutState.confirm)
    else:
        await state.set_state(CheckoutState.address)
        markup = create_inline_kb('pickup', 'back')
        await message.answer(LEXICON['set_address'],
                             reply_markup=markup)


@cart_router.callback_query(F.data == 'back', StateFilter(CheckoutState.address))
async def process_address_back(callback: CallbackQuery, state: FSMContext):
    markup = create_inline_kb('back')
    await callback.message.answer(LEXICON['change_name'].format((await state.get_data())['name']),
                                  reply_markup=markup)
    await state.set_state(CheckoutState.name)
    await callback.answer()


@cart_router.callback_query(F.data == 'pickup', StateFilter(CheckoutState.address))
@cart_router.message(StateFilter(CheckoutState.address))
async def process_address(update: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if isinstance(update, CallbackQuery):
        data['address'] = LEXICON['address_if_pickup']
        await update.answer()
        update = update.message
    else:
        data['address'] = update.text
    await state.set_data(data)
    await state.set_state(CheckoutState.phone)
    markup = create_inline_kb('back')
    await update.answer(LEXICON['set_phone'],
                        reply_markup=markup)


@cart_router.callback_query(F.data == 'back', StateFilter(CheckoutState.phone))
async def process_address_back(callback: CallbackQuery, state: FSMContext):
    markup = create_inline_kb('back')
    await callback.message.answer(LEXICON['change_address'].format((await state.get_data())['address']),
                                  reply_markup=markup)
    await state.set_state(CheckoutState.address)
    await callback.answer()


@cart_router.message(StateFilter(CheckoutState.phone))
async def process_address(message: Message, state: FSMContext):
    data = await state.get_data()
    data['phone'] = message.text
    await state.set_data(data)

    await confirm(message)
    await state.set_state(CheckoutState.confirm)


@cart_router.callback_query(F.data == 'back', StateFilter(CheckoutState.confirm))
async def process_confirm(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutState.phone)
    markup = create_inline_kb('back')
    await callback.message.answer(LEXICON['change_phone'].format((await state.get_data())['phone']),
                                  reply_markup=markup)
    await callback.answer()


@cart_router.callback_query(F.data == 'confirm', StateFilter(CheckoutState.confirm))
async def process_confirm(callback: CallbackQuery, state: FSMContext, admins: list, threshold: int,
                          database: DatabaseManager, bot: Bot):
    enough_money = True  # enough money on the balance sheet
    markup = ReplyKeyboardRemove()
    message = callback.message
    if enough_money:

        logging.info('Deal was made.')
        data = await state.get_data()
        cid = message.chat.id
        products = [idx + '=' + str(quantity)
                    for idx, quantity in database.fetchall('''SELECT idx, quantity FROM cart
        WHERE cid=?''', (cid,))]  # idx=quantity

        database.query('INSERT INTO orders VALUES (?, ?, ?, ?)',
                       (cid, data['name'], data['address'], ' '.join(products)))

        database.query('DELETE FROM cart WHERE cid=?', (cid,))
        markup = create_inline_kb('menu')
        await message.answer(LEXICON['done_to_user'] + LEXICON['user_info'].format(data['name'],
                                                                                            data['address'],
                                                                                            data['phone']),
                             reply_markup=markup)
        for admin_id in admins:
            await bot.send_message(admin_id, LEXICON['done_to_admin'].format(message.from_user.username,
                                                                             message.from_user.id) +
                                   LEXICON['user_info'].format(data['name'], data['address'], data['phone']))
        await checkout(state=state, info_to_admin=True, admins=admins, threshold=threshold, bot=bot)
    else:

        await message.answer(LEXICON['no_money'],
                             reply_markup=markup)

    await state.clear()
    await callback.answer()

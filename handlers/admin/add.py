
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from keyboards.default.markups import *
from states import ProductState, CategoryState
from aiogram.enums.chat_action import ChatAction
from handlers.user.menu import settings
from loader import dp, db, bot
from filters import IsAdmin
from hashlib import md5
from keyboards.inline.products_from_catalog import ProductCb
from keyboards.inline.categories import CategoryCb
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import KeyboardButton, BufferedInputFile

add_product = KeyboardButton(text='➕ Добавить товар')
delete_category = KeyboardButton(text='🗑️ Удалить категорию')


@dp.message(IsAdmin(), F.text == settings.text)
async def process_settings(message: Message):

    markup = InlineKeyboardMarkup()

    for idx, title in db.fetchall('SELECT * FROM categories'):
        markup.inline_keyboard.append([InlineKeyboardButton(
            text=title, callback_data=CategoryCb(id=idx, action='view'))])

    markup.inline_keyboard.append([InlineKeyboardButton(text='+ Добавить категорию', callback_data='add_category')])

    await message.answer('Настройка категорий:', reply_markup=markup)


@dp.callback_query(IsAdmin(), CategoryCb.filter(F.action == 'view'))
async def category_callback_handler(query: CallbackQuery, callback_data: CategoryCb, state: FSMContext):

    category_idx = callback_data.id

    products = db.fetchall('''SELECT * FROM products product
    WHERE product.tag = (SELECT title FROM categories WHERE idx=?)''',
                           (category_idx,))

    await query.message.delete()
    await query.answer('Все добавленные товары в эту категорию.')
    await state.update_data(category_index=category_idx)
    await show_products(query.message, products)


# category


@dp.callback_query(IsAdmin(), F.text == 'add_category')
async def add_category_callback_handler(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer('Название категории?')
    await state.set_state(CategoryState.title)


@dp.message(IsAdmin(), StateFilter(CategoryState.title))
async def set_category_title_handler(message: Message, state: FSMContext):

    category = message.text
    idx = md5(category.encode('utf-8')).hexdigest()
    db.query('INSERT INTO categories VALUES (?, ?)', (idx, category))
    await state.clear()
    await process_settings(message)


@dp.message(IsAdmin(), F.text == delete_category.text)
async def delete_category_handler(message: Message, state: FSMContext):

    data = await state.get_data()
    if 'category_index' in data.keys():

        idx = data['category_index']

        db.query(
            'DELETE FROM products WHERE tag IN (SELECT title FROM categories WHERE idx=?)', (idx,))
        db.query('DELETE FROM categories WHERE idx=?', (idx,))

        await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())
        await process_settings(message)


@dp.message(IsAdmin(), F.text == add_product.text)
async def process_add_product(message: Message, state: FSMContext):
    await state.set_state(ProductState.title)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.keyboard.append(cancel_message)

    await message.answer('Название?', reply_markup=markup)


@dp.message(IsAdmin(), F.text == cancel_message.text, StateFilter(ProductState.title))
async def process_cancel(message: Message, state: FSMContext):

    await message.answer('Ок, отменено!', reply_markup=ReplyKeyboardRemove())
    await state.clear()

    await process_settings(message)


@dp.message(IsAdmin(), F.text == back_message.text, StateFilter(ProductState.title))
async def process_title_back(message: Message):
    await process_add_product(message)


@dp.message(IsAdmin(), StateFilter(ProductState.title))
async def process_title(message: Message, state: FSMContext):
    data = await state.get_data()
    data['title'] = message.text
    await state.set_data(data)
    await state.set_state(ProductState.body)
    await message.answer('Описание?', reply_markup=back_markup())


@dp.message(IsAdmin(), F.text == back_message.text, StateFilter(ProductState.body))
async def process_body_back(message: Message, state: FSMContext):
    await state.set_state(ProductState.title)
    await message.answer(f"Изменить название с <b>{(await state.get_data())['title']}</b>?", reply_markup=back_markup())


@dp.message(IsAdmin(), StateFilter(ProductState.body))
async def process_body(message: Message, state: FSMContext):
    data = await state.get_data()
    data['body'] = message.text
    await state.set_data(data)
    await state.set_state(ProductState.image)
    await message.answer('Фото?', reply_markup=back_markup())


@dp.message(IsAdmin(), StateFilter(ProductState.image), F.photo)
async def process_image_photo(message: Message, state: FSMContext):

    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = (await bot.download_file(file_info.file_path)).read()
    data = await state.get_data()
    data['image'] = downloaded_file
    await state.set_data(data)
    await state.set_state(ProductState.price)
    await message.answer('Цена?', reply_markup=back_markup())


@dp.message(IsAdmin(), StateFilter(ProductState.image), F.text)
async def process_image_url(message: Message, state: FSMContext):

    if message.text == back_message:
        state.set_state(ProductState.body)

        await message.answer(f"Изменить описание с <b>{(await state.get_data())['body']}</b>?",
                             reply_markup=back_markup())

    else:

        await message.answer('Вам нужно прислать фото товара.')


@dp.message(IsAdmin(), lambda message: not message.text.isdigit(), StateFilter(ProductState.price))
async def process_price_invalid(message: Message, state: FSMContext):

    if message.text == back_message:
        state.set_state(ProductState.image)

        await message.answer("Другое изображение?", reply_markup=back_markup())

    else:

        await message.answer('Укажите цену в виде числа!')


@dp.message(IsAdmin(), lambda message: message.text.isdigit(), StateFilter(ProductState.price))
async def process_price(message: Message, state: FSMContext):
    data = await state.get_data()
    data['price'] = message.text
    await state.set_data(data)
    title = data['title']
    body = data['body']
    price = data['price']

    await state.set_state(ProductState.confirm)
    text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price} рублей.'

    markup = check_markup()

    await message.answer_photo(photo=BufferedInputFile(data['image'], filename=text),
                               caption=text,
                               reply_markup=markup)


@dp.message(IsAdmin(), lambda message: message.text not in [back_message.text, all_right_message.text],
            StateFilter(ProductState.confirm))
async def process_confirm_invalid(message: Message):
    await message.answer('Такого варианта не было.')


@dp.message(IsAdmin(), F.text == back_message.text, StateFilter(ProductState.confirm))
async def process_confirm_back(message: Message, state: FSMContext):
    await state.set_state(ProductState.price)

    await message.answer(f"Изменить цену с <b>{(await state.get_data())['price']}</b>?", reply_markup=back_markup())


@dp.message(IsAdmin(), F.text == all_right_message.text, StateFilter(ProductState.confirm))
async def process_confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    title = data['title']
    body = data['body']
    image = data['image']
    price = data['price']

    tag = db.fetchone(
        'SELECT title FROM categories WHERE idx=?', (data['category_index'],))[0]
    idx = md5(' '.join([title, body, price, tag]
                       ).encode('utf-8')).hexdigest()

    db.query('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)',
             (idx, title, body, image, int(price), tag))

    await state.clear()
    await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())
    await process_settings(message)


# delete product


@dp.callback_query(IsAdmin(), ProductCb.filter(F.action == 'delete'))
async def delete_product_callback_handler(query: CallbackQuery, callback_data: ProductCb):

    product_idx = callback_data.id
    db.query('DELETE FROM products WHERE idx=?', (product_idx,))
    await query.answer('Удалено!')
    await query.message.delete()


async def show_products(m, products):

    await bot.send_chat_action(m.chat.id, ChatAction.TYPING)

    for idx, title, body, image, price, tag in products:

        text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price} рублей.'

        markup = InlineKeyboardMarkup()
        markup.inline_keyboard.append([InlineKeyboardButton(
            text='🗑️ Удалить', callback_data=ProductCb(id=idx, action='delete'))])

        await m.answer_photo(photo=BufferedInputFile(image, filename=text),
                             caption=text,
                             reply_markup=markup)

    markup = ReplyKeyboardMarkup()
    markup.keyboard.append([add_product])
    markup.keyboard.append([delete_category])

    await m.answer('Хотите что-нибудь добавить или удалить?', reply_markup=markup)

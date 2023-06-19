from aiogram.types import Message, CallbackQuery, BufferedInputFile
from keyboards.inline.categories import categories_markup, CategoryCb
from keyboards.inline.products_from_catalog import product_markup, ProductCb
from keyboards.default.markups import menu_categories_markup, categories_message
from aiogram.enums.chat_action import ChatAction
from loader import dp, db, bot
from .menu import catalog
from filters import IsUser
from aiogram import F


@dp.message(IsUser(), F.text == catalog.text)
@dp.message(IsUser(), F.text == categories_message.text)
async def process_catalog(message: Message):
    await message.answer('Выберите раздел, чтобы вывести список товаров:',
                         reply_markup=categories_markup())


@dp.callback_query(IsUser(), CategoryCb.filter(F.action == 'view'))
async def category_callback_handler(query: CallbackQuery, callback_data: CategoryCb):

    products = db.fetchall('''SELECT * FROM products product
    WHERE product.tag = (SELECT title FROM categories WHERE idx=?) 
    AND product.idx NOT IN (SELECT idx FROM cart WHERE cid = ?)''',
                           (callback_data.id, query.message.chat.id))

    await query.answer('Все доступные товары.')
    await show_products(query.message, products)


@dp.callback_query(IsUser(), ProductCb.filter(F.action == 'add'))
async def add_product_callback_handler(query: CallbackQuery, callback_data: ProductCb):

    db.query('INSERT INTO cart VALUES (?, ?, 1)',
             (query.message.chat.id, callback_data.id))

    await query.answer('Товар добавлен в корзину!')
    await query.message.delete()


async def show_products(m, products):

    if len(products) == 0:

        await m.answer('Здесь ничего нет 😢')

    else:

        await bot.send_chat_action(m.chat.id, ChatAction.TYPING)

        for idx, title, body, image, price, _ in products:

            markup = product_markup(idx, price)
            text = f'<b>{title}</b>\n\n{body}'

            await m.answer_photo(photo=BufferedInputFile(image, filename=text),
                                 caption=text,
                                 reply_markup=markup)
        await m.answer(text='Что вы хотите сделать?',
                       reply_markup=menu_categories_markup())

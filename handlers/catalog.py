from aiogram.types import CallbackQuery
from keyboards.categories import categories_markup, CategoryCb
from keyboards.products_from_catalog import ProductCb
from aiogram import F
from aiogram import Router, Bot
from handlers.handler_functions import show_products
from database.storage import DatabaseManager
from lexicon import LEXICON

# Инициализируем роутер уровня модуля
catalog_router: Router = Router()


@catalog_router.callback_query(F.data == 'catalog')
async def process_catalog(callback: CallbackQuery, database: DatabaseManager):
    await callback.message.answer(LEXICON['catalog'],
                                  reply_markup=categories_markup(database))
    await callback.answer()


@catalog_router.callback_query(CategoryCb.filter(F.action == 'view'))
async def category_callback_handler(callback: CallbackQuery, callback_data: CategoryCb,
                                    bot: Bot, database: DatabaseManager):
    message = callback.message
    products = database.fetchall('''SELECT * FROM products product
    WHERE product.tag = (SELECT title FROM categories WHERE idx=?) 
    AND product.idx NOT IN (SELECT idx FROM cart WHERE cid = ?)''',
                                 (callback_data.id, message.chat.id))

    await callback.answer(LEXICON['view'])
    await show_products(message, products, bot)


@catalog_router.callback_query(ProductCb.filter(F.action == 'add'))
async def add_product_callback_handler(callback: CallbackQuery, callback_data: ProductCb, database: DatabaseManager):
    message = callback.message
    database.query('INSERT INTO cart VALUES (?, ?, 1)',
                   (message.chat.id, callback_data.id))

    await callback.answer(LEXICON['add'])
    await message.delete()

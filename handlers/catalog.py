from aiogram.types import CallbackQuery
from keyboards.categories import categories_markup, CategoryCb
from keyboards.products_from_catalog import ProductCb
from aiogram import F
from aiogram import Router, Bot
from handlers.handler_functions import show_products
from database.storage import DatabaseManager
from lexicon import LEXICON
from aiogram.fsm.context import FSMContext

# Инициализируем роутер уровня модуля
catalog_router: Router = Router()


@catalog_router.callback_query(F.data == 'catalog')
async def process_catalog(callback: CallbackQuery, database: DatabaseManager, state: FSMContext):
    await state.update_data(start_index=0)
    await state.update_data(category_idx=0)
    await callback.message.answer(LEXICON['catalog'],
                                  reply_markup=categories_markup(database))
    await callback.answer()


@catalog_router.callback_query(CategoryCb.filter(F.action == 'view'))
async def category_callback_handler(callback: CallbackQuery, callback_data: CategoryCb,
                                    bot: Bot, database: DatabaseManager, state: FSMContext):
    message = callback.message
    products = database.fetchall('''SELECT * FROM products product
    WHERE product.tag = (SELECT title FROM categories WHERE idx=?) 
    AND product.idx NOT IN (SELECT idx FROM cart WHERE cid = ?)''',
                                 (callback_data.id, message.chat.id))
    await state.update_data(category_idx=callback_data.id)
    await callback.answer(LEXICON['view'])
    await show_products(message, products, bot, state)


@catalog_router.callback_query(F.data == 'pagination_forward')
@catalog_router.callback_query(F.data == 'pagination_back')
async def pagination_forward_callback_handler(callback: CallbackQuery, bot: Bot, state: FSMContext,
                                              database: DatabaseManager):
    data = await state.get_data()
    if callback.data == "pagination_back":
        start_index = data["start_index"]
        await state.update_data(start_index=start_index-20)
    products = database.fetchall('''SELECT * FROM products product
        WHERE product.tag = (SELECT title FROM categories WHERE idx=?) 
        AND product.idx NOT IN (SELECT idx FROM cart WHERE cid = ?)''',
                                 (data["category_idx"], callback.message.chat.id))
    await show_products(callback.message, products, bot, state)
    await callback.answer()


@catalog_router.callback_query(ProductCb.filter(F.action == 'add'))
async def add_product_callback_handler(callback: CallbackQuery, callback_data: ProductCb, database: DatabaseManager):
    message = callback.message
    database.query('INSERT INTO cart VALUES (?, ?, 1)',
                   (message.chat.id, callback_data.id))

    await callback.answer(LEXICON['add'])
    await message.delete()

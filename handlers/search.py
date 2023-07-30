from aiogram import Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram import F
from handlers.handler_functions import show_products
from database.storage import DatabaseManager
from aiogram.fsm.context import FSMContext
from lexicon import LEXICON
from keyboards.kb_generator import create_inline_kb
from aiogram.filters import StateFilter
from states import SearchState

# Инициализируем роутер уровня модуля
search_router: Router = Router()


@search_router.callback_query(F.data == 'search_form')
async def search_form_callback_handler(callback: CallbackQuery, bot: Bot, state: FSMContext, database: DatabaseManager):
    await callback.message.answer(LEXICON['search'])
    await state.set_state(SearchState.search)
    await callback.answer()


@search_router.message(StateFilter(SearchState.search))
async def search_callback_handler(message: Message, bot: Bot, state: FSMContext, database: DatabaseManager):
    search_query = f"%{message.text.lower()}%"  # Добавляем % для выполнения поиска по части строки
    products = database.fetchall('''SELECT * FROM products product
            WHERE mylower(product.title) LIKE ? AND product.idx NOT IN (SELECT idx FROM cart WHERE cid = ?)''',
                                 (search_query, message.chat.id))
    if len(products):
        await show_products(message, products, bot, state)
    else:
        menu_markup = create_inline_kb('catalog', 'cart', 'search_form')
        await message.answer(LEXICON['search_nothing'], reply_markup=menu_markup)
    await state.clear()


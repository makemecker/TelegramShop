from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram import F
from keyboards.kb_generator import create_inline_kb
from aiogram import Router
from lexicon import LEXICON
from aiogram.fsm.context import FSMContext

# Инициализируем роутер уровня модуля
menu_router: Router = Router()


@menu_router.message(Command(commands=['start', 'menu']))
@menu_router.callback_query(F.data == 'menu')
async def user_menu(update: Message | CallbackQuery, state: FSMContext):
    if isinstance(update, CallbackQuery):
        await update.answer()
        update = update.message
    markup = create_inline_kb('catalog', 'cart', 'search_form')
    await update.answer(LEXICON['/menu'], reply_markup=markup)

from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram import F
from keyboards.kb_generator import create_inline_kb
from aiogram import Router

# Инициализируем роутер уровня модуля
menu_router: Router = Router()


@menu_router.message(Command(commands=['start', 'menu']))
@menu_router.callback_query(F.data == 'menu')
async def user_menu(update: Message | CallbackQuery):
    if isinstance(update, CallbackQuery):
        await update.answer()
        update = update.message
    markup = create_inline_kb('catalog', 'cart')
    await update.answer('Меню', reply_markup=markup)

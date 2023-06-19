from aiogram.types import Message, ReplyKeyboardMarkup
from loader import dp
from filters import IsAdmin, IsUser
from keyboards.default.markups import menu_message
from aiogram.filters import Command
from aiogram.types import KeyboardButton
from aiogram import F

catalog = KeyboardButton(text='🛍️ Каталог')
cart = KeyboardButton(text='🛒 Корзина')
delivery_status = KeyboardButton(text='🚚 Статус заказа')

settings = KeyboardButton(text='⚙️ Настройка каталога')
orders_kb = KeyboardButton(text='🚚 Заказы')
questions_kb = KeyboardButton(text='❓ Вопросы')


@dp.message(IsAdmin(), Command(commands=['start', 'menu']))
async def admin_menu(message: Message):
    markup = ReplyKeyboardMarkup(keyboard=[[settings], [questions_kb, orders_kb]], selective=True)
    await message.answer('Меню', reply_markup=markup)


@dp.message(IsUser(), Command(commands=['start', 'menu']))
@dp.message(IsUser(), F.text == menu_message.text)
async def user_menu(message: Message):
    markup = ReplyKeyboardMarkup(keyboard=[[catalog], [cart], [delivery_status]], selective=True)
    await message.answer('Меню', reply_markup=markup)

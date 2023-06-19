from aiogram.types import InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from loader import db
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CategoryCb(CallbackData, prefix="category"):
    id: str
    action: str


def categories_markup():
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for idx, title in db.fetchall('SELECT * FROM categories'):
        kb_builder.row(InlineKeyboardButton(text=title, callback_data=CategoryCb(id=idx, action='view').pack()))

    return kb_builder.as_markup()

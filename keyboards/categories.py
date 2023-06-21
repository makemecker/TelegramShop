from aiogram.types import InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.storage import DatabaseManager


class CategoryCb(CallbackData, prefix="category"):
    id: str
    action: str


def categories_markup(database: DatabaseManager):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for idx, title in database.fetchall('SELECT * FROM categories'):
        kb_builder.row(InlineKeyboardButton(text=title, callback_data=CategoryCb(id=idx, action='view').pack()))

    return kb_builder.as_markup()

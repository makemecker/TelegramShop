from aiogram.types import InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.kb_generator import BUTTONS


class ProductCb(CallbackData, prefix="product"):
    id: str
    action: str


def product_markup(idx='', price=0):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.add(InlineKeyboardButton(text=BUTTONS['add'].format(price),
                                        callback_data=ProductCb(id=idx, action='add').pack()))

    return kb_builder.as_markup()

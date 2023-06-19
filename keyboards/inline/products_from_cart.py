from aiogram.types import InlineKeyboardButton
from keyboards.inline.products_from_catalog import ProductCb
from aiogram.utils.keyboard import InlineKeyboardBuilder


def product_markup(idx, count):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    back_btn = InlineKeyboardButton(text='⬅️', callback_data=ProductCb(id=idx, action='decrease').pack())
    back10_btn = InlineKeyboardButton(text='↖️', callback_data=ProductCb(id=idx, action='decrease10').pack())
    count_btn = InlineKeyboardButton(text=count, callback_data=ProductCb(id=idx, action='count').pack())
    next_btn = InlineKeyboardButton(text='➡️', callback_data=ProductCb(id=idx, action='increase').pack())
    next10_btn = InlineKeyboardButton(text='↗️', callback_data=ProductCb(id=idx, action='increase10').pack())
    kb_builder.row(back10_btn, back_btn, count_btn, next_btn, next10_btn)

    count50_btn = InlineKeyboardButton(text='50 шт', callback_data=ProductCb(id=idx, action='count50').pack())
    count100_btn = InlineKeyboardButton(text='100 шт', callback_data=ProductCb(id=idx, action='count100').pack())
    kb_builder.row(count50_btn, count100_btn)

    reset_btn = InlineKeyboardButton(text='Удалить товар из корзины ❌',
                                     callback_data=ProductCb(id=idx, action='reset').pack())
    kb_builder.row(reset_btn)

    return kb_builder.as_markup()

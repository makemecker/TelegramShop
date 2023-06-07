from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

product_cb = CallbackData('product', 'id', 'action')


def product_markup(idx, count):

    global product_cb

    markup = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('⬅️', callback_data=product_cb.new(id=idx, action='decrease'))
    back10_btn = InlineKeyboardButton('↖️', callback_data=product_cb.new(id=idx, action='decrease10'))
    count_btn = InlineKeyboardButton(count, callback_data=product_cb.new(id=idx, action='count'))
    next_btn = InlineKeyboardButton('➡️', callback_data=product_cb.new(id=idx, action='increase'))
    next10_btn = InlineKeyboardButton('↗️', callback_data=product_cb.new(id=idx, action='increase10'))
    markup.row(back10_btn, back_btn, count_btn, next_btn, next10_btn)

    count50_btn = InlineKeyboardButton('50 шт', callback_data=product_cb.new(id=idx, action='count50'))
    count100_btn = InlineKeyboardButton('100 шт', callback_data=product_cb.new(id=idx, action='count100'))
    markup.row(count50_btn, count100_btn)

    reset_btn = InlineKeyboardButton('Удалить товар из корзины ❌', callback_data=product_cb.new(id=idx, action='reset'))
    markup.row(reset_btn)

    return markup

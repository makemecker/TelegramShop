from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

back_message = KeyboardButton(text='👈 Назад')
confirm_message = KeyboardButton(text='✅ Подтвердить заказ')
all_right_message = KeyboardButton(text='✅ Все верно')
cancel_message = KeyboardButton(text='🚫 Отменить')
categories_message = KeyboardButton(text='К категориям товаров 🛍️')
menu_message = KeyboardButton(text='В меню 🍪')
cart_message = KeyboardButton(text='К корзине 🛒')


def confirm_markup():
    markup = ReplyKeyboardMarkup(keyboard=[[confirm_message], [back_message]], resize_keyboard=True, selective=True)

    return markup


def back_markup():
    markup = ReplyKeyboardMarkup(keyboard=[[back_message]], resize_keyboard=True, selective=True)

    return markup


def check_markup():
    markup = ReplyKeyboardMarkup(keyboard=[[back_message, all_right_message]], resize_keyboard=True, selective=True)

    return markup


def submit_markup():
    markup = ReplyKeyboardMarkup(keyboard=[[cancel_message, all_right_message]], resize_keyboard=True, selective=True)

    return markup


def menu_categories_markup():
    markup = ReplyKeyboardMarkup(keyboard=[[menu_message], [categories_message], [cart_message]], resize_keyboard=True,
                                 selective=True)

    return markup

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

BUTTONS: dict[str, str] = {
    'catalog': '🛍️ Посмотреть каталог',
    'cart': '🛒 Проверить корзину',
    'status': '🚚 Статус заказа',
    'menu': 'В меню 🍪',
    'order': '📦 Оформить заказ',
    'all_right': '✅ Все верно',
    'back': '👈 Назад',
    'confirm': '✅ Подтвердить заказ',
    'pickup': '📦 Самовывоз',
    '-1': '⬅️',
    '-10': '↖️',
    '+1': '➡️',
    '+10': '↗️',
    'count50': '50 шт',
    'count100': '100 шт',
    'reset': 'Удалить товар из корзины ❌',
    'add': 'Добавить в корзину - {}₽',
    'pagination_forward': 'Посмотреть следующие 10 товаров ➡️',
    'pagination_back': 'Посмотреть предыдущие 10 товаров ⬅️',
    }


# Функция для формирования инлайн-клавиатуры на лету
def create_inline_kb(*args: str,
                     **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=BUTTONS[button] if button in BUTTONS else button,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=1)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()

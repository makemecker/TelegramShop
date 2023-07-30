from config import load_config

PICKUP_ADDRESS: str = load_config().pickup_address

LEXICON: dict[str, str] = {
    'empty_cart': 'Ваша корзина пуста.',
    'to_registration': 'Перейти к оформлению?',
    'count': 'Количество - {}',
    'set_name': 'Укажите, пожалуйста, Ваше имя',
    'change_name': 'Укажите новое имя вместо ранее указанного (<b> {} </b>)?',
    'set_address': f'Укажите, пожалуйста, адрес доставки или выберите Самовывоз.\nСамовывоз осуществляется по адресу: '
                   f'{PICKUP_ADDRESS}',
    'change_address': 'Изменить адрес: <b> {} </b>?',
    'address_if_pickup': f'Самовывоз ({PICKUP_ADDRESS})',
    'set_phone': 'Укажите, пожалуйста, телефон для связи',
    'change_phone': 'Изменить телефон: <b> {} </b>?',
    'done_to_user': 'Отлично! Наш Менеджер свяжется с Вами в ближайшее время 🚀',
    'done_to_admin': "Оформлен новый заказ!\n"
                     "Пользователь: @{}\n"
                     "User_id: {}",
    'user_info': '\nИмя: <b> {} </b>' +
                 '\nАдрес: <b> {} </b>' +
                 '\nТелефон: <b> {} </b>\n',
    'no_money': 'У вас недостаточно денег на счете. Пополните баланс!',
    'catalog': 'Выберите раздел, чтобы вывести список товаров:',
    'view': 'Все доступные товары.',
    'add': 'Товар добавлен в корзину!',
    'status_no': 'У вас нет активных заказов.',
    'status_warehouse': ' лежит на складе.',
    'status_on_way': ' уже в пути!',
    'status_delivered': ' прибыл и ждет вас на почте!',
    'threshold_to_user': '\n\n Сумма заказа составляет менее {}₽, поэтому доставка заказа платная. '
                         'Надо определить стоимость доставки до клиента',
    'threshold_to_admin': '\n\n Сумма заказа составляет менее {}₽, поэтому доставка заказа платная. '
                          'Стоимость доставки Менеджер сообщит дополнительно.',
    'order_info': '{}\nОбщая сумма заказа: {}₽. {}',
    'check': 'Убедитесь, что все правильно оформлено и подтвердите заказ.',
    'nothing': 'Здесь ничего нет 😢',
    'submenu': 'Что Вы хотите сделать?',
    '/menu': '|                  Меню           |',
    '/help': 'По всем вопросам можно обратиться к нашему менеджеру:\n @helpyoumanager',
    'other': 'Для продолжения наберите команду /menu',
    "search": 'Введите, пожалуйста, название товара, который Вы хотите найти',
    "search_nothing": "К сожалению товара с таким названием не найдено. Предлагаем Вам взглянуть на наш каталог "
                      ", где Вы сможете найти интересующий Вас товар."
}

LEXICON_COMMANDS: dict[str, str] = {
    '/menu': 'Показать меню магазина',
    '/help': 'Обратиться к менеджеру'
}

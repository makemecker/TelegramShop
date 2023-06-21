from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command


# Инициализируем роутер уровня модуля
other_router: Router = Router()


# todo: Изменить никнейм buketoff на Manager
# todo: Изменить команду /sos на /help через BotFather
@other_router.message(Command(commands=['help']))
async def help_command(message: Message):
    await message.answer('По всем вопросам можно обратиться к нашему менеджеру:\n @helpyoumanager')


@other_router.message()
async def any_unmark_message(message: Message):
    await message.answer('Для продолжения наберите команду /menu')

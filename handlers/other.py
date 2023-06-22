from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from lexicon import LEXICON

# Инициализируем роутер уровня модуля
other_router: Router = Router()


@other_router.message(Command(commands=['help']))
async def help_command(message: Message):
    await message.answer(LEXICON['/help'])


@other_router.message()
async def any_unmark_message(message: Message):
    await message.answer(LEXICON['other'])

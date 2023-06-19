
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from keyboards.default.markups import all_right_message, cancel_message, submit_markup
from aiogram.types import Message
from states import SosState
from filters import IsUser
from loader import dp, db
from aiogram.filters import Command, StateFilter
from aiogram import F


@dp.message(Command(commands='sos'))
async def cmd_sos(message: Message, state: FSMContext):
    await state.set_state(SosState.question)
    await message.answer('В чем суть проблемы? Опишите как можно детальнее и администратор обязательно вам ответит.',
                         reply_markup=ReplyKeyboardRemove())


@dp.message(StateFilter(SosState.question))
async def process_question(message: Message, state: FSMContext):
    data = state.get_data()
    data['question'] = message.text
    await state.set_data(data)

    await message.answer('Убедитесь, что все верно.', reply_markup=submit_markup())
    await state.set_state(SosState.submit)


@dp.message(lambda message: message.text not in [cancel_message.text, all_right_message.text],
            StateFilter(SosState.submit))
async def process_price_invalid(message: Message):
    await message.answer('Такого варианта не было.')


@dp.message(F.text == cancel_message.text, StateFilter(SosState.submit))
async def process_cancel(message: Message, state: FSMContext):
    await message.answer('Отменено!', reply_markup=ReplyKeyboardRemove())
    await state.clear()


@dp.message(F.text == all_right_message.text, StateFilter(SosState.submit))
async def process_submit(message: Message, state: FSMContext):

    cid = message.chat.id

    if db.fetchone('SELECT * FROM questions WHERE cid=?', (cid,)) is None:
        data = await state.get_data()
        db.query('INSERT INTO questions VALUES (?, ?)',
                 (cid, data['question']))

        await message.answer('Отправлено!', reply_markup=ReplyKeyboardRemove())

    else:

        await message.answer('Превышен лимит на количество задаваемых вопросов.', reply_markup=ReplyKeyboardRemove())

    await state.clear()


@dp.message(IsUser())
async def any_unmark_message(message: Message):
    await message.answer('Для продолжения наберите команду /menu')

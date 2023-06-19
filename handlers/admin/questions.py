
from handlers.user.menu import questions_kb
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
from keyboards.default.markups import all_right_message, cancel_message, submit_markup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.enums.chat_action import ChatAction
from states import AnswerState
from loader import dp, db, bot
from filters import IsAdmin
from aiogram import F
from aiogram.filters import StateFilter


class QuestionCb(CallbackData, prefix="question"):
    cid: str
    action: str


@dp.message(IsAdmin(), F.text == questions_kb.text)
async def process_questions(message: Message):

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    questions = db.fetchall('SELECT * FROM questions')

    if len(questions) == 0:

        await message.answer('Нет вопросов.')

    else:

        for cid, question in questions:

            markup = InlineKeyboardMarkup()
            markup.inline_keyboard.append([InlineKeyboardButton(
                text='Ответить', callback_data=QuestionCb(cid=cid, action='answer'))])

            await message.answer(question, reply_markup=markup)


@dp.callback_query(IsAdmin(), QuestionCb.filter(F.action == 'answer'))
async def process_answer(query: CallbackQuery, callback_data: QuestionCb, state: FSMContext):
    data = await state.get_data()
    data['cid'] = callback_data.cid
    await state.set_data(data)

    await query.message.answer('Напиши ответ.', reply_markup=ReplyKeyboardRemove())
    await state.set_state(AnswerState.answer)


@dp.message(IsAdmin(), StateFilter(AnswerState.answer))
async def process_submit(message: Message, state: FSMContext):
    data = await state.get_data()
    data['answer'] = message.text
    await state.set_data(data)

    await state.set_state(AnswerState.submit)
    await message.answer('Убедитесь, что не ошиблись в ответе.', reply_markup=submit_markup())


@dp.message(IsAdmin(), F.text == cancel_message.text, StateFilter(AnswerState.submit))
async def process_send_answer(message: Message, state: FSMContext):
    await message.answer('Отменено!', reply_markup=ReplyKeyboardRemove())
    await state.clear()


@dp.message(IsAdmin(), F.text == all_right_message.text, StateFilter(AnswerState.submit))
async def process_send_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    answer = data['answer']
    cid = data['cid']

    question = db.fetchone(
        'SELECT question FROM questions WHERE cid=?', (cid,))[0]
    db.query('DELETE FROM questions WHERE cid=?', (cid,))
    text = f'Вопрос: <b>{question}</b>\n\nОтвет: <b>{answer}</b>'

    await message.answer('Отправлено!', reply_markup=ReplyKeyboardRemove())
    await bot.send_message(cid, text)

    await state.clear()

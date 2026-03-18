import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен твоего бота от BotFather
TOKEN = "8562139672:AAGYRcU2lwFwWc8tLjHNbOfuIHaCu7cc9rc"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Состояния для теста
class QuizStates(StatesGroup):
    question_idx = State()  # Номер текущего вопроса
    scores = State()        # Накопленные баллы

# Список вопросов Шкалы Спанн-Фишер
QUESTIONS = [
    "Мне трудно принимать решения.",
    "Мне трудно сказать «нет» тем, кто просит меня о помощи.",
    "Мне трудно принимать комплименты или подарки.",
    "Я чувствую себя виноватым, когда трачу деньги на себя.",
    "Я не чувствую себя «целостным» без близких отношений.",
    "Я часто беспокоюсь о том, нравлюсь ли я другим.",
    "Мне трудно делиться своими истинными чувствами.",
    "Когда другим больно, я чувствую их боль как свою.",
    "Я часто ставлю чужие потребности выше своих.",
    "Я чувствую себя ответственным за чувства других.",
    "Я часто пытаюсь угадать, чего другие хотят от меня.",
    "Мне трудно просить о том, что мне нужно.",
    "Я часто остаюсь в отношениях, которые мне вредят.",
    "Моя самооценка зависит от мнения других людей.",
    "Я склонен брать на себя больше дел, чем могу выполнить.",
    "Я чувствую, что должен всё контролировать для безопасности."
]

def get_quiz_keyboard():
    builder = InlineKeyboardBuilder()
    for i in range(1, 7):
        builder.button(text=str(i), callback_data=f"score_{i}")
    builder.adjust(3) # Кнопки в два ряда по 3 штуки
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Пройти тест", callback_data="start_quiz")
    kb.button(text="💬 Написать специалисту", url="https://t.me/gunintherapy")
    kb.adjust(1)

    await message.answer(
        "Ты живёшь чужой жизнью.\n\n"
        "Пытаешься помочь, спасти, контролировать...\n"
        "А в итоге — теряешь себя.\n\n"
        "Это не просто забота.\n"
        "Это созависимость.\n\n"
        "👇 Ниже будет тест из 16 вопросов\n\n"
        "Оцени каждое утверждение:\n\n"
        "1 — совсем не про меня\n"
        "6 — полностью про меня\n\n"
        "Отвечай честно. Здесь нет правильных ответов.\n\n"
        "Готов начать?",
        reply_markup=kb.as_markup()
    )

@dp.message(Command("quiz"))
async def start_quiz(message: types.Message, state: FSMContext):
    await state.set_state(QuizStates.question_idx)
    await state.update_data(question_idx=0, scores=0)

    await message.answer(
        f"Вопрос 1: {QUESTIONS[0]}",
        reply_markup=get_quiz_keyboard()
    )


@dp.callback_query(F.data == "start_quiz")
async def start_quiz_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.question_idx)
    await state.update_data(question_idx=0, scores=0)

    await callback.message.answer(
        f"Вопрос 1: {QUESTIONS[0]}",
        reply_markup=get_quiz_keyboard()
    )

    await callback.answer()
    )

    await callback.answer()
    await state.set_state(QuizStates.question_idx)
    await state.update_data(question_idx=0, scores=0)
    await message.answer(f"Вопрос 1: {QUESTIONS[0]}", reply_markup=get_quiz_keyboard())

@dp.callback_query(F.data.startswith("score_"))
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    q_idx = data['question_idx']
    current_scores = data['scores']
    
    # Прибавляем балл из callback_data
    score = int(callback.data.split("_")[1])
    new_scores = current_scores + score
    next_q_idx = q_idx + 1

    if next_q_idx < len(QUESTIONS):
        # Переход к следующему вопросу
        await state.update_data(question_idx=next_q_idx, scores=new_scores)
        await callback.message.edit_text(
            f"Вопрос {next_q_idx + 1}: {QUESTIONS[next_q_idx]}",
            reply_markup=get_quiz_keyboard()
        )
    else:
        # Финал теста
        result_text = get_interpretation(new_scores)
        await callback.message.edit_text(f"Тест завершен!\n\nВаш результат: {new_scores} баллов.\n\n{result_text}")
        await state.clear()
    
    await callback.answer()

def get_interpretation(score):
    if 16 <= score <= 34:
        return "🟢 **Низкий уровень созависимости.** Вы обладаете здоровыми границами."
    elif 35 <= score <= 55:
        return "🟡 **Средний уровень созависимости.** Есть склонность забывать о своих интересах."
    else:
        return "🔴 **Высокий уровень созависимости.** Рекомендуется обратить внимание на свои границы или обратиться к психологу."

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

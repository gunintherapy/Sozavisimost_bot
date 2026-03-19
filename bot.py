import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен (берется из Railway)
TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# -----------------------
# Состояния
# -----------------------
class QuizStates(StatesGroup):
    question_idx = State()
    scores = State()

# -----------------------
# Вопросы
# -----------------------
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

# -----------------------
# Клавиатура
# -----------------------
def get_quiz_keyboard():
    builder = InlineKeyboardBuilder()
    for i in range(1, 7):
        builder.button(text=str(i), callback_data=f"score_{i}")
    builder.adjust(3)
    return builder.as_markup()

# -----------------------
# /start
# -----------------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Пройти тест", callback_data="start_quiz")
    kb.button(text="💬 Написать специалисту", url="https://t.me/voshodkrsk")
    kb.adjust(1)

    await message.answer(
        "Ты живёшь чужой жизнью.\n\n"
        "Пытаешься помочь, спасти, контролировать...\n"
        "А в итоге — теряешь себя.\n\n"
        "Это не просто забота.\n"
        "Это созависимость.\n\n"
        "👇 Ниже будет тест из 16 вопросов\n\n"
        "Оцени каждое утверждение:\n"
        "1 — совсем не про меня\n"
        "6 — полностью про меня\n\n"
        "Отвечай честно. Здесь нет правильных ответов.\n\n"
        "Готов начать?",
        reply_markup=kb.as_markup()
    )

# -----------------------
# Старт теста через кнопку
# -----------------------
@dp.callback_query(F.data == "start_quiz")
async def start_quiz(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.question_idx)
    await state.update_data(question_idx=0, scores=0)

    await callback.message.answer(
        f"Вопрос 1: {QUESTIONS[0]}",
        reply_markup=get_quiz_keyboard()
    )

    await callback.answer()

# -----------------------
# Ответы
# -----------------------
@dp.callback_query(F.data.startswith("score_"))
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    q_idx = data.get('question_idx', 0)
    current_scores = data.get('scores', 0)

    score = int(callback.data.split("_")[1])
    new_scores = current_scores + score
    next_q_idx = q_idx + 1

    if next_q_idx < len(QUESTIONS):
        await state.update_data(question_idx=next_q_idx, scores=new_scores)

        await callback.message.edit_text(
            f"Вопрос {next_q_idx + 1}: {QUESTIONS[next_q_idx]}",
            reply_markup=get_quiz_keyboard()
        )

    else:
        result_text = get_interpretation(new_scores)

        kb = InlineKeyboardBuilder()
        kb.button(
            text="💬 Разобрать мою ситуацию",
            url="https://t.me/voshodkrsk"
        )
        kb.button(
            text="📊 Пройти тест снова",
            callback_data="start_quiz"
        )
        kb.adjust(1)

        await callback.message.edit_text(
            f"Тест завершен!\n\n"
            f"Ваш результат: {new_scores} баллов.\n\n"
            f"{result_text}\n\n"
            f"👉 Это не просто цифры.\n"
            f"Это модель поведения, которая влияет на твою жизнь.\n\n"
            f"Напиши мне в личку:\n"
            f"👉 Я из бота\n\n"
            f"Я задам пару вопросов и скажу, что с этим делать.",
            reply_markup=kb.as_markup()
        )

        await state.clear()

    await callback.answer()

# -----------------------
# Интерпретация
# -----------------------
def get_interpretation(score: int) -> str:
    if 16 <= score <= 34:
        return (
            "🟢 У тебя пока есть опора на себя.\n\n"
            "Но будь внимателен — созависимость подкрадывается незаметно."
        )

    elif 35 <= score <= 55:
        return (
            "🟡 Ты уже начинаешь терять себя.\n\n"
            "Чужие эмоции становятся важнее твоих.\n"
            "Ты подстраиваешься и терпишь.\n\n"
            "Это постепенно тебя разрушает."
        )

    else:
        return (
            "🔴 Ты живёшь чужой жизнью.\n\n"
            "Пытаешься контролировать и спасать.\n"
            "Но по факту — разрушаешь себя.\n\n"
            "И остановиться уже сложно."
        )

# -----------------------
# Запуск
# -----------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

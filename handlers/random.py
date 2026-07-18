from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from constants import RANDOM_IMAGE_PATH
from utils.logger import show_user_action
from services.openai_service import openai_service
from telegram.ext import CallbackContext


def random_keyboard():
    """Inline-кнопки под сообщением с фактом."""

    keyboard = [
        [InlineKeyboardButton("Хочу ещё факт", callback_data="random_more")],
        [InlineKeyboardButton("Закончить", callback_data="random_end")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def random_fact(update, context: CallbackContext):
    """
    Обработчик команды /random.
    Отправляет изображение + случайный факт от ChatGPT + кнопки.
    """

    user = update.effective_user
    show_user_action(user, "/random")

    try:
        with open(RANDOM_IMAGE_PATH, 'rb') as photo:
            await update.message.reply_photo(
                photo,
                caption="Интересный факт для вас!"
            )
    except FileNotFoundError:
        await update.message.reply_text("🖼️ [Изображение не найдено]")

    response = openai_service.request_random_fact()

    await update.message.reply_text(
        f"Случайный факт:\n\n{response}",
        reply_markup=random_keyboard(),
    )


async def random_fact_more(update, context: CallbackContext):
    """
    Обработчик кнопки «Хочу ещё факт».
    Работает так же, как команда /random, но через callback_query.
    """

    query = update.callback_query
    await query.answer()

    response = openai_service.request_random_fact()

    await query.message.reply_text(
        f"Случайный факт:\n\n{response}",
        reply_markup=random_keyboard(),
    )


async def random_fact_end(update, context: CallbackContext):
    """
    Обработчик кнопки «Закончить».
    Показывает сообщение о завершении просмотра фактов.
    """

    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Спасибо за внимание! ✨\n\n"
        "Можешь вернуться к другим командам: /gpt, /talk, /quiz, /voice, /help."
    )

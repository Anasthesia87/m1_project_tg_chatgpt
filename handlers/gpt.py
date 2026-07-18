from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from constants import RANDOM_IMAGE_GPT_PATH, WAITING_FOR_PROMPT
from services.openai_service import openai_service
from utils.logger import show_user_action, logger


async def gpt(update: Update, context: CallbackContext) -> None:
    """
    Обработчик команды /gpt.
    Отправляет изображение и предлагает ввести вопрос.
    """

    user = update.effective_user
    show_user_action(user, action="/gpt")

    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="cancel_gpt")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open(RANDOM_IMAGE_GPT_PATH, 'rb') as photo:
            await update.message.reply_photo(
                photo,
                caption="Задайте ваш вопрос для GPT (или нажмите '❌ Отмена'):",
                reply_markup=reply_markup
            )

    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        await update.message.reply_text("Не удалось отправить изображение, но можно задать вопрос текстом.")

    return WAITING_FOR_PROMPT


async def handler_prompt(update: Update, context: CallbackContext) -> None:
    """
    Обработка текста пользователя.
    Отправляет запрос в ChatGPT и возвращает ответ.
    """

    user = update.effective_user
    show_user_action(user, action="GPT_ЗАПРОС")

    user_input = update.message.text

    await update.message.reply_text("🔍 Ищу ответ…")

    response = openai_service.request_gpt_plain(user_input)

    keyboard = [
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_gpt")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Ответ на ваш вопрос:\n\n{response}",
        reply_markup=reply_markup)
    return WAITING_FOR_PROMPT


async def cancel_gpt(update: Update, context: CallbackContext) -> None:
    """Обработчик кнопки «Отмена»."""
    query = update.callback_query
    await query.answer()

    openai_service.reset_gpt_history()

    await query.edit_message_caption(
        "❌ Диалог с ChatGPT завершен.\n\n"
        "Используйте /start для начала.")

    return ConversationHandler.END


async def cancel_gpt_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /cancel во время диалога с GPT"""
    openai_service.reset_gpt_history()

    await update.message.reply_text(
        "❌ Диалог с ChatGPT завершен.\n\n"
        "Используйте /start для начала.")

    return ConversationHandler.END

from telegram import Update
from telegram.ext import CallbackContext
from utils.logger import show_user_action
from constants import HELP_MESSAGE_FILE


async def help(update: Update, context: CallbackContext) -> str:
    """Обработчик команды /help"""
    user = update.effective_user
    show_user_action(user, action="/help")

    try:
        with open(HELP_MESSAGE_FILE, "r", encoding='UTF8') as f:
            text = f.read()
    except FileNotFoundError:
        return "Файл помощи не найден. Обратись к разработчику бота."

    await update.message.reply_text(text)

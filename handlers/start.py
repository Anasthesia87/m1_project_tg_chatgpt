from telegram import Update
from telegram.ext import CallbackContext
from utils.logger import show_user_action


async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    show_user_action(user, action="/start")

    await update.message.reply_text(
        "Привет! Я бот с ChatGPT 😊\n\n"
        "Что я умею:\n"
        "/gpt – обычное общение с ChatGPT\n"
        "/talk – поговорить с персонажами из сериала «Клон»\n"
        "/quiz – пройти квиз по выбранной теме\n"
        "/random – получить случайный интересный факт\n"
        "/voice – голосовой ChatGPT (отправьте голосовое сообщение)\n"
        "/translate – перевести текст на выбранный язык\n"
        "/help – подробная помощь по боту\n"
    )

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from constants import TRANSLATE_WAITING_FOR_LANGUAGE, TRANSLATE_WAITING_FOR_TEXT
from prompts import TRANSLATE_LANGUAGES
from utils import show_user_action, logger
from services.openai_service import openai_service


async def translate_start(update: Update, context: CallbackContext) -> None:
    """
    Команда /translate.
    Показывает кнопки выбора языка.
    """

    user = update.effective_user
    show_user_action(user, action="/translate")
    logger.info(f"Пользователь {user.username} ({user.id}) запустил команду /translate!")

    buttons = [
        InlineKeyboardButton(name, callback_data=code)
        for code, name in TRANSLATE_LANGUAGES.items()
    ]

    keyboard = []
    for i in range(0, len(buttons), 2):
        row = [buttons[i]]
        if i + 1 < len(buttons):
            row.append(buttons[i + 1])
        keyboard.append(row)

    keyboard.append(
        [InlineKeyboardButton("❌ Закончить", callback_data="translate_finish")]
    )

    await update.message.reply_text(
        "🌍 Выберите язык, на который нужно перевести текст:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    context.user_data["translate_language_code"] = None
    context.user_data["translate_language_name"] = None

    return TRANSLATE_WAITING_FOR_LANGUAGE


async def translate_selected_language(update: Update, context: CallbackContext) -> None:
    """
    Обработка выбора языка.
    Сохраняет выбранный язык и просит текст для перевода.
    """

    query = update.callback_query
    await query.answer()

    code = query.data
    if code == "translate_finish":
        await query.edit_message_text(
            "Перевод завершён.\n\nМожешь снова воспользоваться командами:\n"
            "/gpt – обычное общение с ChatGPT\n"
            "/talk – поговорить с персонажами\n"
            "/quiz – пройти квиз\n"
            "/random – случайный факт\n"
            "/voice – голосовой режим\n"
            "/translate – переводчик\n"
            "/help – помощь"
        )
        return ConversationHandler.END

    language_name = TRANSLATE_LANGUAGES.get(code)
    if not language_name:
        await query.edit_message_text("❌ Не удалось определить язык.")
        return ConversationHandler.END

    context.user_data["translate_language_code"] = code
    context.user_data["translate_language_name"] = language_name

    await query.edit_message_text(
        text=f"Вы выбрали язык: {language_name}.\n\n"
             "Отправьте текст, который нужно перевести:",
    )

    return TRANSLATE_WAITING_FOR_TEXT


async def translate_process_text(update: Update, context: CallbackContext) -> None:
    """
    Принимает текст пользователя, отправляет его в GPT для перевода
    и возвращает результат с кнопками «Сменить язык» и «Закончить».
    """

    user_text = update.message.text
    target_language = context.user_data.get("translate_language_name")

    if not target_language:
        await update.message.reply_text(
            "Сначала выберите язык через /translate."
        )
        return ConversationHandler.END

    await update.message.reply_text("🔄 Перевожу текст…")

    translated = await openai_service.request_translation(user_text, target_language)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌍 Сменить язык", callback_data="translate_change_language")],
        [InlineKeyboardButton("❌ Закончить", callback_data="translate_finish")],
    ])

    await update.message.reply_text(
        f"📤 Оригинал:\n{user_text}\n\n"
        f"📥 Перевод ({target_language}):\n{translated}",
        reply_markup=keyboard,
    )

    return TRANSLATE_WAITING_FOR_TEXT


async def translate_change_language(update: Update, context: CallbackContext) -> None:
    """
    Кнопка «Сменить язык».
    Возвращает пользователя к выбору языка, не завершая переводчик.
    """

    query = update.callback_query
    await query.answer()

    buttons = [
        InlineKeyboardButton(name, callback_data=code)
        for code, name in TRANSLATE_LANGUAGES.items()
    ]

    keyboard = []
    for i in range(0, len(buttons), 2):
        row = [buttons[i]]
        if i + 1 < len(buttons):
            row.append(buttons[i + 1])
        keyboard.append(row)

    keyboard.append(
        [InlineKeyboardButton("❌ Закончить", callback_data="translate_finish")]
    )

    await query.edit_message_text(
        "🌍 Выберите новый язык для перевода:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    context.user_data["translate_language_code"] = None
    context.user_data["translate_language_name"] = None

    return TRANSLATE_WAITING_FOR_LANGUAGE

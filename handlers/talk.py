from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from constants import TALK_IMAGE_PATH, WAITING_FOR_PERSON, TALKING_WITH_PERSON
from prompts import PERSONA_PROMPTS, WAIT_MESSAGES
from services.openai_service import openai_service
from utils.logger import show_user_action, logger


async def talk(update: Update, context: CallbackContext) -> None:
    """
    Обработчик команды /talk
    1. Отправляет заранее заготовленное изображение
    2. Предлагает выбор из персонажей сериала «Клон» с помощью кнопок
    """

    user = update.effective_user
    show_user_action(user, action="/talk")

    keyboard = [
        [InlineKeyboardButton("Дядя Али", callback_data='uncle_ali')],
        [InlineKeyboardButton("Жади", callback_data='jadi')],
        [InlineKeyboardButton("Саид", callback_data='said')],
        [InlineKeyboardButton("Иветти", callback_data='ivette')],
        [InlineKeyboardButton("❌ Закончить", callback_data='talk_finish')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open(TALK_IMAGE_PATH, 'rb') as photo:
            await update.message.reply_photo(
                photo,
                caption="Выберите персонажа из сериала «Клон», с которым хотите поговорить:",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        await update.message.reply_text(
            "Выберите персонажа из сериала «Клон», с которым хотите поговорить:",
            reply_markup=reply_markup
        )

    return WAITING_FOR_PERSON


async def select_person(update: Update, context: CallbackContext) -> None:
    """
    Обработка нажатия на кнопку с именем персонажа.
    Устанавливает промт выбранной личности и сохраняет её ключ.
    """

    user = update.effective_user
    show_user_action(user, action="/select_person")

    query = update.callback_query
    await query.answer()

    persona_key = query.data

    if persona_key == "talk_finish":
        return await talk_finish(update, context)

    persona_prompt = PERSONA_PROMPTS.get(persona_key)
    if not persona_prompt:
        await query.edit_message_caption("❌ Не удалось найти персонажа.")
        return ConversationHandler.END

    context.user_data["character_name"] = persona_key
    context.user_data["active_system_prompt"] = persona_prompt

    openai_service.reset_persona_history(persona_key)

    human_name_map = {
        "uncle_ali": "Дядя Али",
        "jadi": "Жади",
        "said": "Саид",
        "ivette": "Иветти",
    }
    human_name = human_name_map.get(persona_key, persona_key)

    await query.edit_message_caption(
        caption=f"Вы выбрали: {human_name}\n\nНапишите, что хотите спросить у персонажа:",
        reply_markup=None,
    )

    return TALKING_WITH_PERSON


async def talk_handler(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    show_user_action(user, action="/talk_message")

    persona_key = context.user_data.get("character_name")
    if not persona_key:
        await update.message.reply_text("Контекст потерян. Выберите персонажа снова через /talk.")
        return ConversationHandler.END

    prompt = update.message.text

    wait_text = WAIT_MESSAGES.get(persona_key, "Персонаж собирается с мыслями...")
    await update.message.reply_text(wait_text)

    response = openai_service.request_gpt_persona(
        text=prompt,
        persona_name=persona_key,
    )

    keyboard = [
        [InlineKeyboardButton("❌ Закончить", callback_data="talk_finish")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(response, reply_markup=reply_markup)

    return TALKING_WITH_PERSON


async def talk_finish(update: Update, context: CallbackContext) -> None:
    """
    Обработчик кнопки 'Закончить'.
    Работает так же, как команда /start: показывает приветственное сообщение.
    """

    user = update.effective_user
    show_user_action(user, action="finish")

    query = update.callback_query
    await query.answer()

    persona_key = context.user_data.get("character_name")
    human_name_map = {
        "uncle_ali": "Дядя Али",
        "jadi": "Жади",
        "said": "Саид",
        "ivette": "Иветти",
    }
    name = human_name_map.get(persona_key, "выбранным персонажем")

    if persona_key:
        openai_service.reset_persona_history(persona_key)

    end_text = (
        f"✅ Диалог с {name} завершён!\n\n"
        "Привет! Я бот с ChatGPT!\n\n"
        "Доступные команды:\n"
        "/start - Показать это сообщение\n"
        "/random - Получить случайный факт\n"
        "/gpt - Общаться с ChatGPT\n"
        "/talk - Поговорить с персонажем из «Клона»\n"
        "/quiz - Пройти квиз\n"
        "/voice – голосовой ChatGPT (отправьте голосовое сообщение)\n"
        "/translate – перевести текст на выбранный язык\n"
        "/help - Помощь"
    )

    message = query.message
    if message.photo:
        await query.edit_message_caption(caption=end_text, reply_markup=None)
    else:
        await query.edit_message_text(text=end_text, reply_markup=None)

    for key in ("character_name", "active_system_prompt"):
        context.user_data.pop(key, None)

    return ConversationHandler.END

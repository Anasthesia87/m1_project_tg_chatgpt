from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from utils.logger import show_user_action
from services.openai_service import openai_service
from constants import QUIZ_WAITING_FOR_TOPIC, QUIZ_WAITING_FOR_ANSWER, QUIZ_IMAGE_PATH
from prompts import QUIZ_TOPIC_HINTS, build_quiz_question_prompt, build_quiz_check_prompt


async def quiz_start(update: Update, context: CallbackContext) -> None:
    """
    Команда /quiz.
    Отсылает заранее заготовленное изображение и предлагает выбор темы с кнопками.
    """

    user = update.effective_user
    show_user_action(user, "/quiz")

    buttons = [
        InlineKeyboardButton(
            title.split(":")[0],
            callback_data=topic_key
        )
        for topic_key, title in QUIZ_TOPIC_HINTS.items()
    ]

    keyboard = []
    for i in range(0, len(buttons), 2):
        line = [buttons[i]]
        if i + 1 < len(buttons):
            line.append(buttons[i + 1])
        keyboard.append(line)

    keyboard.append(
        [InlineKeyboardButton("❌ Закончить квиз", callback_data="quiz_finish")]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open(QUIZ_IMAGE_PATH, "rb") as photo:
            await update.message.reply_photo(
                photo,
                caption="🎲 Выберите тему для квиза:",
                reply_markup=reply_markup,
            )
    except FileNotFoundError:
        await update.message.reply_text(
            "🎲 Выберите тему для квиза:\n\n🖼️ [Изображение не найдено]",
            reply_markup=reply_markup,
        )

    context.user_data["quiz_correct"] = 0
    context.user_data["quiz_total"] = 0
    context.user_data["quiz_topic_key"] = None
    context.user_data["quiz_topic_title"] = None
    context.user_data["quiz_question"] = None

    return QUIZ_WAITING_FOR_TOPIC


async def quiz_select_topic(update: Update, context: CallbackContext) -> None:
    """
    Обработка выбора темы.
    Генерирует первый вопрос по выбранной теме через OpenAI.
    """

    query = update.callback_query
    await query.answer()

    topic_key = query.data
    if topic_key == "quiz_finish":
        return await quiz_finish(update, context)

    full_hint = QUIZ_TOPIC_HINTS.get(topic_key)
    if not full_hint:
        await query.edit_message_text("❌ Не удалось определить тему квиза.")
        return ConversationHandler.END

    topic_title = full_hint.split(":")[0]

    context.user_data["quiz_topic_key"] = topic_key
    context.user_data["quiz_topic_title"] = topic_title

    chat_id = update.effective_chat.id

    prompt = build_quiz_question_prompt(topic_key, topic_title)
    question = openai_service.request_quiz(
        chat_id=chat_id,
        text=prompt,
        topic_key=topic_key,
    )

    context.user_data["quiz_question"] = question

    message = query.message
    text = f"Тема: {topic_title}\n\n{question}\n\nНапишите ваш ответ сообщением:"

    if message.photo:
        await query.edit_message_caption(
            caption=text,
            reply_markup=None,
        )
    else:
        await query.edit_message_text(
            text=text,
            reply_markup=None,
        )

    return QUIZ_WAITING_FOR_ANSWER


async def quiz_process_answer(update: Update, context: CallbackContext) -> None:
    """
    Принимает текстовый ответ пользователя, отправляет его на проверку в OpenAI,
    показывает результат и счёт, предлагает кнопки.
    """
    user_answer = update.message.text

    topic_key = context.user_data.get("quiz_topic_key")
    topic_title = context.user_data.get("quiz_topic_title")
    question = context.user_data.get("quiz_question")

    if not (topic_key and topic_title and question):
        await update.message.reply_text("Сначала выберите тему через /quiz.")
        return ConversationHandler.END

    chat_id = update.effective_chat.id

    prompt = build_quiz_check_prompt(
        topic_key=topic_key,
        topic_title=topic_title,
        question=question,
        user_answer=user_answer,
    )
    result_text = openai_service.request_quiz(
        chat_id=chat_id,
        text=prompt,
        topic_key=topic_key,
    )

    total = context.user_data.get("quiz_total", 0) + 1
    context.user_data["quiz_total"] = total

    lower = result_text.lower()
    correct = context.user_data.get("quiz_correct", 0)

    if "правильно" in lower and "неправильно" not in lower:
        correct += 1
        context.user_data["quiz_correct"] = correct

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ещё вопрос по этой теме", callback_data="quiz_more")],
        [InlineKeyboardButton("Сменить тему", callback_data="quiz_change_topic")],
        [InlineKeyboardButton("❌ Закончить квиз", callback_data="quiz_finish")],
    ])

    await update.message.reply_text(
        f"{result_text}\n\nВаш счёт: {correct} из {total} правильных ответов.",
        reply_markup=keyboard,
    )

    return QUIZ_WAITING_FOR_ANSWER


async def quiz_more(update: Update, context: CallbackContext) -> None:
    """
    Кнопка «Ещё вопрос по этой теме».
    Генерирует новый вопрос по текущей теме.
    """
    query = update.callback_query
    await query.answer()

    topic_key = context.user_data.get("quiz_topic_key")
    topic_title = context.user_data.get("quiz_topic_title")
    if not (topic_key and topic_title):
        await query.edit_message_text("Тема потеряна, запустите /quiz заново.")
        return ConversationHandler.END

    chat_id = query.message.chat_id

    prompt = build_quiz_question_prompt(topic_key, topic_title)
    question = openai_service.request_quiz(
        chat_id=chat_id,
        text=prompt,
        topic_key=topic_key,
    )

    context.user_data["quiz_question"] = question

    await query.edit_message_text(
        text=f"Новый вопрос по теме «{topic_title}»:\n\n{question}\n\nНапишите ваш ответ:",
    )

    return QUIZ_WAITING_FOR_ANSWER


async def quiz_change_topic(update: Update, context: CallbackContext) -> None:
    """
    Кнопка «Сменить тему».
    Возвращает пользователя к выбору темы.
    """
    query = update.callback_query
    await query.answer()

    buttons = [
        InlineKeyboardButton(
            title.split(":")[0],
            callback_data=topic_key,
        )
        for topic_key, title in QUIZ_TOPIC_HINTS.items()
    ]

    keyboard = []
    for i in range(0, len(buttons), 2):
        line = [buttons[i]]
        if i + 1 < len(buttons):
            line.append(buttons[i + 1])
        keyboard.append(line)

    keyboard.append(
        [InlineKeyboardButton("❌ Закончить квиз", callback_data="quiz_finish")]
    )

    await query.edit_message_text(
        text="🎲 Выберите новую тему для квиза:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    context.user_data["quiz_topic_key"] = None
    context.user_data["quiz_topic_title"] = None
    context.user_data["quiz_question"] = None

    return QUIZ_WAITING_FOR_TOPIC


async def quiz_finish(update: Update, context: CallbackContext) -> None:
    """
    Кнопка «❌ Закончить квиз».
    Показывает итоговый счёт и очищает данные квиза.
    """
    query = update.callback_query
    await query.answer()

    correct = context.user_data.get("quiz_correct", 0)
    total = context.user_data.get("quiz_total", 0)

    end_text = (
        f"✅ Квиз завершён!\n\n"
        f"Ваш итоговый счёт: {correct} из {total}.\n\n"
        "Доступные команды:\n"
        "/start - Приветствие\n"
        "/random - Случайный факт\n"
        "/gpt - Общаться с ChatGPT\n"
        "/talk - Поговорить с персонажем\n"
        "/quiz - Пройти квиз ещё раз\n"
        "/voice – голосовой ChatGPT (отправьте голосовое сообщение)\n"
        "/translate – перевести текст на выбранный язык\n"
        "/help - Помощь"
    )

    message = query.message
    if message.photo:
        await query.edit_message_caption(
            caption=end_text,
            reply_markup=None,
        )
    else:
        await query.edit_message_text(
            text=end_text,
            reply_markup=None,
        )

    for key in (
            "quiz_correct",
            "quiz_total",
            "quiz_topic_key",
            "quiz_topic_title",
            "quiz_question",
    ):
        context.user_data.pop(key, None)

    return ConversationHandler.END

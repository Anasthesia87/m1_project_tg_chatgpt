"""
Глобальные константы для Telegram-бота.
"""

# ===== Пути к файлам =====
HELP_MESSAGE_FILE = "help_message.txt"

RANDOM_IMAGE_PATH = "assets/random_image.jpg"
RANDOM_IMAGE_GPT_PATH = "assets/image_for_gpt.jpg"
TALK_IMAGE_PATH = "assets/talk_image.jpg"
QUIZ_IMAGE_PATH = "assets/image_for_quiz.jpg"


# ===== Состояния для ConversationHandler =====
# Сценарий /gpt
WAITING_FOR_PROMPT = 1  # ждём текст запроса к GPT
WAITING_FOR_PERSON = 2  # ждём выбор "персонажа"/стиля ответа

# Сценарий /talk
TALKING_WITH_PERSON = 3  # диалог с "персонажем"

# Сценарий /quiz
QUIZ_WAITING_FOR_TOPIC = 4  # ждём тему для квиза
QUIZ_WAITING_FOR_ANSWER = 5  # ждём ответ пользователя на вопрос квиза

# Сценарий /translate
TRANSLATE_WAITING_FOR_LANGUAGE = 6  # ждём выбор языка перевода
TRANSLATE_WAITING_FOR_TEXT = 7  # ждём текст для перевода

"""
Telegram ChatGPT Bot
Основной файл запуска бота
"""
import fix_pydub
import sys
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ApplicationBuilder,
)
from config import config
from constants import *
from utils.logger import logger
from handlers import *


def main():
    try:
        logger.info("Запускаем бота...")
        logger.info(f"Модель OpenAI: {config.OPENAI_MODEL}")

        app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

        # Базовые команды
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help))

        # ==========ChatGPT интерфейс: /gpt ===========
        app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("gpt", gpt)],
                states={
                    WAITING_FOR_PROMPT: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, handler_prompt),
                        CallbackQueryHandler(cancel_gpt, pattern="^cancel_gpt$"),
                    ],
                },
                fallbacks=[
                    CallbackQueryHandler(cancel_gpt, pattern="^cancel_gpt$"),
                    CommandHandler("cancel", cancel_gpt_command),
                ],
                allow_reentry=True,
            )
        )

        # ===== Рандомный факт: /random =====
        app.add_handler(CommandHandler("random", random_fact))
        app.add_handler(CallbackQueryHandler(random_fact_more, pattern="^random_more$"))
        app.add_handler(CallbackQueryHandler(random_fact_end, pattern="^random_end$"))

        # ===== Диалог с известной личностью: /talk =====
        app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("talk", talk)],
                states={
                    WAITING_FOR_PERSON: [CallbackQueryHandler(select_person)],
                    TALKING_WITH_PERSON: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, talk_handler),
                        CallbackQueryHandler(talk_finish, pattern="^talk_finish$"),
                    ],
                },
                fallbacks=[
                    CommandHandler("finish", talk_finish),
                ],
                allow_reentry=True,
            )
        )

        # ===== Квиз: /quiz =====
        app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("quiz", quiz_start)],
                states={
                    QUIZ_WAITING_FOR_TOPIC: [
                        CallbackQueryHandler(quiz_select_topic),
                    ],
                    QUIZ_WAITING_FOR_ANSWER: [
                        MessageHandler(
                            filters.TEXT & ~filters.COMMAND, quiz_process_answer
                        ),
                        CallbackQueryHandler(quiz_more, pattern="^quiz_more$"),
                        CallbackQueryHandler(
                            quiz_change_topic, pattern="^quiz_change_topic$"
                        ),
                        CallbackQueryHandler(quiz_finish, pattern="^quiz_finish$"),
                    ],
                },
                fallbacks=[CallbackQueryHandler(quiz_finish, pattern="^quiz_finish$")],
                allow_reentry=True,
            )
        )

        # # Обработка текстовых сообщений
        # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        #
        # Обработка голосовых сообщений
        app.add_handler(CommandHandler("voice", voice))
        app.add_handler(MessageHandler(filters.VOICE, voice))

        # ===== Переводчик: /translate =====
        app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("translate", translate_start)],
                states={
                    TRANSLATE_WAITING_FOR_LANGUAGE: [
                        CallbackQueryHandler(translate_selected_language),
                    ],
                    TRANSLATE_WAITING_FOR_TEXT: [
                        MessageHandler(
                            filters.TEXT & ~filters.COMMAND, translate_process_text
                        ),
                        CallbackQueryHandler(
                            translate_change_language,
                            pattern="^translate_change_language$",
                        ),
                        CallbackQueryHandler(
                            translate_selected_language, pattern="^translate_finish$"
                        ),
                    ],
                },
                fallbacks=[
                    CallbackQueryHandler(
                        translate_selected_language, pattern="^translate_finish$"
                    )
                ],
                allow_reentry=True,
            )
        )

        logger.info("Бот готов к работе, запускаю polling...")
        app.run_polling()

    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

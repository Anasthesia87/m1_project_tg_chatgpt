from pathlib import Path
from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext
from services.audio_service import local_transcribe, local_tts
from utils.logger import show_user_action, logger
from services.openai_service import openai_service


async def voice(update: Update, context: CallbackContext) -> None:
    """
    Принимает голосовое сообщение, распознаёт текст локально,
    отправляет его GPT и возвращает ответ в виде аудио.
    """

    user = update.effective_user
    show_user_action(user, action="/voice")
    logger.info(f"Пользователь {user.username} ({user.id}) запустил команду /voice!")

    if not update.message or not update.message.voice:
        await update.message.reply_text(

            "🎙️ Голосовой ChatGPT.\n\n"
            "Теперь отправьте голосовое сообщение с вопросом, и я отвечу вам голосом.\n\n"
            "Чтобы вернуться к обычному режиму — просто используйте другие команды (/start, /help) "
            "или пишите текстовые сообщения."
        )
        return

    audio_dir = Path("audio")
    audio_dir.mkdir(exist_ok=True)

    voice = update.message.voice
    voice_id = voice.file_id

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = audio_dir / f"voice_{user.id}_{ts}.wav"

    file = await context.bot.get_file(voice_id)
    await file.download_to_drive(input_path)

    await update.message.reply_text("🎙️ Обрабатываю ваш голос…")
    transcribed_text = await local_transcribe(str(input_path))

    if not transcribed_text:
        await update.message.reply_text(
            "Не удалось распознать голос. Попробуйте ещё раз.\n\n"
            "Можете снова отправить голосовое сообщение или выйти из голосового режима, "
            "просто продолжив переписку как обычно."
        )
        return

    await update.message.reply_text(f"📝 Вы сказали:\n{transcribed_text}")

    gpt_reply = openai_service.request_gpt_plain(transcribed_text)

    await update.message.reply_text(f"💬 Ответ ChatGPT:\n{gpt_reply}")

    output_path = audio_dir / f"reply_{user.id}_{ts}.mp3"
    tts_path = await local_tts(gpt_reply, str(output_path), lang="ru")

    if not tts_path:
        await update.message.reply_text("Не удалось создать аудио-ответ. Но текстовый ответ выше.")
        return

    with open(tts_path, "rb") as audio_file:
        await update.message.reply_voice(
            audio_file,
            caption="🔊 Голосовой ответ ChatGPT",
        )

    logger.info(f"Голосовой ChatGPT (локальный аудио) обработал запрос пользователя {user.id}")

from pathlib import Path
from gtts import gTTS
from faster_whisper import WhisperModel
from utils import logger

model = WhisperModel("base", device="cpu", compute_type="int8")


async def local_transcribe(file_path: str) -> str:
    """
    Локальное распознавание речи через faster-whisper.
    Возвращает распознанный текст одним строковым результатом.
    """
    try:
        logger.info(f"Распознаю аудио через faster-whisper: {file_path}")

        segments, info = model.transcribe(
            file_path,
            language="ru",
            beam_size=5,
        )

        parts = []
        for segment in segments:
            parts.append(segment.text)

        text = " ".join(parts).strip()
        logger.info(f"Локальное распознавание завершено, текст: {text!r}")

        return text
    except Exception as e:
        logger.error(f"Ошибка локального распознавания аудио: {e}", exc_info=True)
        return ""


async def local_tts(text: str, output_path: str, lang: str = "ru") -> str:
    """
    Локальная озвучка текста с помощью gTTS.
    """
    try:
        tts = gTTS(text=text, lang=lang)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        tts.save(str(out))
        logger.info(f"Сгенерирован локальный аудио-ответ: {out}")
        return str(out)
    except Exception as e:
        logger.error(f"Ошибка локального TTS: {e}", exc_info=True)
        return ""

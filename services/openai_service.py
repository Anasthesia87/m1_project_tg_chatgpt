from openai import OpenAI
from config import config
from prompts import *
from utils.logger import logger


class OpenAIService:
    """Сервис для работы с OpenAI API с раздельной историей по режимам."""

    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
        self.max_output_tokens = config.OPENAI_MAX_TOKENS
        self.temperature = config.OPENAI_TEMPERATURE
        self.reasoning = {"effort": config.REASONING_EFFORT}

        logger.info(f"OpenAIService инициализирован с моделью {self.model}")

        # История для обычного GPT (/gpt)
        self.gpt_history: list[dict] = []

        # История для диалогов с личностями: persona_name -> list[messages]
        self.persona_histories: dict[str, list[dict]] = {}

        # История для квиза: chat_id -> list[messages]
        self.quiz_histories: dict[int, list[dict]] = {}

    # ---------- Рандомный факт (/random) ----------

    def request_random_fact(self) -> str:
        """
        Генерация одного случайного познавательного факта.
        История не хранится: каждый факт независим.
        """
        try:
            messages = [
                {"role": "system", "content": RANDOM_FACT_SYSTEM_PROMPT},
                {"role": "user", "content": "Расскажи мне один случайный факт."},
            ]

            response = self.client.responses.create(
                model=self.model,
                input=messages,
                max_output_tokens=self.max_output_tokens,
                reasoning={"effort": config.REASONING_EFFORT},
            )

            response_text = response.output_text
            logger.info("Получен рандомный факт от GPT")

            return response_text

        except Exception as e:
            logger.error(f"Ошибка при запросе рандомного факта: {e}", exc_info=True)
            return "Ошибка при генерации рандомного факта. Попробуйте ещё раз."

    # ---------- Обычный GPT (/gpt) ----------

    def request_gpt_plain(self, text: str) -> str:
        """
        Обычный диалог с ChatGPT.
        Использует GPT_SYSTEM_PROMPT и хранит историю в self.gpt_history.
        """

        try:
            if not self.gpt_history:
                self.gpt_history.append(
                    {
                        "role": "system",
                        "content": GPT_SYSTEM_PROMPT,
                    }
                )

            self.gpt_history.append({"role": "user", "content": text})

            response = self.client.responses.create(
                model=self.model,
                input=self.gpt_history,
                max_output_tokens=self.max_output_tokens,
                reasoning={"effort": config.REASONING_EFFORT},
            )

            answer = response.output_text
            self.gpt_history.append({"role": "assistant", "content": answer})

            logger.info("Получен ответ от GPT (plain)")
            return answer

        except Exception as e:
            logger.error(f"Ошибка запроса к GPT (plain): {e}", exc_info=True)
            return "Произошла ошибка при запросе к ChatGPT. Попробуйте ещё раз."

    def reset_gpt_history(self) -> None:
        """Сброс истории обычного GPT-диалога."""
        self.gpt_history = []

    # ---------- Диалог с личностью (/talk) ----------
    def request_gpt_persona(self, text: str, persona_name: str) -> str:
        """
        Диалог с выбранной личностью.
        Использует промпт из PERSONA_PROMPTS и историю по persona_name.
        """

        try:
            persona_prompt = PERSONA_PROMPTS.get(persona_name, "")
            history = self.persona_histories.setdefault(persona_name, [])

            if not history:
                # первый системный промпт — стиль выбранной личности
                history.append({"role": "system", "content": persona_prompt})

            history.append({"role": "user", "content": text})

            response = self.client.responses.create(
                model=self.model,
                input=history,
                max_output_tokens=self.max_output_tokens,
                reasoning={"effort": config.REASONING_EFFORT},
            )

            answer = response.output_text
            history.append({"role": "assistant", "content": answer})

            logger.info(f"Получен ответ от GPT (persona: {persona_name})")
            return answer

        except Exception as e:
            logger.error(f"Ошибка запроса к GPT (persona): {e}", exc_info=True)
            return "Персонаж сейчас молчит. Попробуйте задать вопрос ещё раз."

    def reset_persona_history(self, persona_name: str) -> None:
        """Сброс истории конкретной личности."""
        self.persona_histories[persona_name] = []

    # ---------- Квиз (/quiz) ----------
    def request_quiz(self, chat_id: int, text: str, topic_key: str) -> str:
        """
        Диалог для квиза.
        - chat_id: ID чата, чтобы хранить историю по пользователю
        - text: промт (запрос вопроса или проверка ответа)
        - topic_key: ключ темы (movies, music, art, literature, programming,
                     space, mythology, animals, food, fashion)

        Использует:
        - QUIZ_SYSTEM_PROMPT — общие правила квиза;
        - QUIZ_TOPIC_HINTS[topic_key] — описание выбранной темы.
        """
        try:
            history = self.quiz_histories.setdefault(chat_id, [])

            if not history:
                history.append({"role": "system", "content": QUIZ_SYSTEM_PROMPT})

                hint = QUIZ_TOPIC_HINTS.get(topic_key, "")
                if hint:
                    topic_prompt = f"Тема квиза: {hint}"
                    history.append({"role": "system", "content": topic_prompt})

            history.append({"role": "user", "content": text})

            response = self.client.responses.create(
                model=self.model,
                input=history,
                max_output_tokens=self.max_output_tokens,
                reasoning={"effort": config.REASONING_EFFORT},
            )

            answer = response.output_text
            history.append({"role": "assistant", "content": answer})

            logger.info(
                f"Получен ответ от GPT (quiz, chat_id={chat_id}, topic={topic_key})"
            )
            return answer

        except Exception as e:
            logger.error(f"Ошибка запроса к GPT (quiz): {e}", exc_info=True)
            return "Не удалось получить ответ от ChatGPT для квиза. Попробуйте ещё раз."

    def reset_quiz_history(self, chat_id: int) -> None:
        """Сброс истории квиза для конкретного пользователя."""
        self.quiz_histories[chat_id] = []

    async def request_translation(self, text: str, target_language: str) -> str:
        """
        Перевод текста на указанный язык с помощью GPT.
        target_language: например, 'Английский'.
        """

        try:
            messages = [
                {
                    "role": "system",
                    "content": TRANSLATE_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"Переведи следующий текст на {target_language}:\n\n{text}",
                },
            ]

            response = self.client.responses.create(
                model=self.model,
                input=messages,
                max_output_tokens=self.max_output_tokens,
                reasoning={"effort": config.REASONING_EFFORT},
            )
            translated = response.output_text.strip()
            logger.info(f"Получен перевод на язык: {target_language}")
            return translated

        except Exception as e:
            logger.error(f"Ошибка перевода текста: {e}", exc_info=True)
            return "Не удалось выполнить перевод. Попробуйте ещё раз."


openai_service = OpenAIService()

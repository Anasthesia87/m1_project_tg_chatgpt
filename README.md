# JR_PYTHON_12 — Telegram ChatGPT бот

Telegram-бот, который умеет общаться как ChatGPT, разговаривать голосом, проводить квизы, переводить текст и общаться с персонажами из сериала «Клон».

👉 Попробовать бота в Telegram: [@JR_PYTHON_12_bot](https://t.me/JR_PYTHON_12_bot)


## Возможности бота

- `/gpt` — обычное общение с ChatGPT.  
  Пишите любые вопросы, мысли и просьбы — бот отвечает текстом.

- `/talk` — общение с персонажами из сериала «Клон».  
  Сначала приходит картинка, затем бот предлагает выбрать героя по кнопке, после чего можно задавать ему вопросы.

- `/quiz` — квиз по выбранной теме.  
  Выберите тему, отвечайте на вопросы, используйте кнопки  
  «Ещё вопрос», «Сменить тему» и «Закончить квиз».

- `/random` — случайный интересный факт.  
  Каждый раз — новый короткий факт.

- `/translate` — перевод текста.  
  Сначала выберите целевой язык, затем отправьте текст — бот переведёт его на выбранный язык.

- `/voice` — голосовое общение с ChatGPT.  
  Отправьте голосовое сообщение — бот распознаёт речь, отправляет запрос к ChatGPT и вернёт ответ текстом и голосом.  
  После ответа появляется кнопка «✅ Закончить голосовой режим», чтобы выйти из сценария.

- `/start` — показывает приветствие и главное меню.  
- `/help` — выводит справку из `help_message.txt` со всеми командами.


## Стек и зависимости

Основные технологии:

- Python 3.13+
- [python-telegram-bot](https://python-telegram-bot.org/) — асинхронный интерфейс к Telegram Bot API
- OpenAI API — для работы с моделями (например, `gpt-5.4-nano`)
- faster-whisper — локальное распознавание речи (Speech-to-Text)
- TTS (pyttsx3 / gTTS) — озвучка ответов
- Логирование через `utils.logger`


## Структура проекта

```text
.
├── bot.py              # точка входа, создание Application, регистрация хендлеров
├── config.py           # чтение переменных окружения (TELEGRAM_TOKEN, OPENAI_API_KEY и др.)
├── constants.py        # пути к файлам, состояния ConversationHandler и пр.
├── fix_pydub.py        # заглушка/фиксы для pydub/audioop
├── help_message.txt    # текст справки для /help
├── prompts.py          # заготовки промптов для GPT-сценариев
├── README.md
├── requirements.txt    # зависимости проекта
├── assets/             # изображения для /gpt, /quiz, /talk
│   ├── image_for_gpt.jpg
│   ├── image_for_quiz.jpg
│   ├── random_image.jpg
│   └── talk_image.jpg
├── handlers/           # обработчики команд /start, /help, /gpt, /quiz, /random, /talk, /translate, /voice
│   ├── gpt.py
│   ├── help.py
│   ├── quiz.py
│   ├── random.py
│   ├── start.py
│   ├── talk.py
│   ├── translate.py
│   ├── voice.py
│   └── __init__.py
├── services/           # сервисы для работы с OpenAI и аудио
│   ├── audio_service.py    # S2T (faster-whisper / Whisper API) и TTS
│   ├── openai_service.py   # обёртка вокруг OpenAI client (ChatGPT, квизы, перевод и т.п.)
│   └── __init__.py
├── utils/
│   ├── logger.py       # настройка логирования
│   └── __init__.py
└── .env                # локальные секреты (в .gitignore, не коммитится)
```


## Установка и запуск локально

1. Клонировать репозиторий:

   ```bash
   git clone https://github.com/Anasthesia87/m1_project_tg_chatgpt.git
   cd m1_project_tg_chatgpt
   ```

2. Создать и активировать виртуальное окружение:

   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. Установить зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Создать файл `.env` в корне проекта и указать ключи:

   ```env
   TELEGRAM_TOKEN=8791058877:...    # токен Telegram-бота
   OPENAI_API_KEY=sk-...            # ключ OpenAI API
   ```

5. Запустить бота:

   ```bash
   python bot.py
   ```

Бот запустит long polling и начнёт обрабатывать команды в Telegram.


## Развёртывание на Railway (бесплатный хостинг)

Проект адаптирован для деплоя на Railway с long polling: достаточно, чтобы контейнер выполнял `python bot.py`.

### Шаги

1. **Подготовить репозиторий**  
   Убедитесь, что изменения закоммичены и запушены в GitHub (`main`/`master`).

2. **Создать проект на Railway**  
   - Зайти на [railway.app](https://railway.app).  
   - Создать новый проект → **Deploy from GitHub repo**.  
   - Выбрать репозиторий `Anasthesia87/m1_project_tg_chatgpt`.

3. **Настроить сборку и запуск**  
   - Build command:  
     ```bash
     pip install -r requirements.txt
     ```  
   - Start command:  
     ```bash
     python bot.py
     ```

4. **Настроить переменные окружения** (Variables).
   В разделе Variables сервиса добавить:

   ```env
   TELEGRAM_TOKEN=8791058877:...   # токен бота
   OPENAI_API_KEY=sk-...           # ключ OpenAI API
   ```

   Эти имена должны совпадать с переменными в `config.py`.

5. **Деплой**  
   - Нажать Deploy / Redeploy.  
   - Railway соберёт контейнер, установит зависимости и запустит `python bot.py`.  
   - В логах сервиса появится строка вроде:  
     `OpenAIService инициализирован с моделью gpt-5.4-nano`.

После этого бот будет доступен в Telegram по ссылке: [@JR_PYTHON_12_bot](https://t.me/JR_PYTHON_12_bot), и будет работать 24/7 в рамках лимитов бесплатного плана Railway.

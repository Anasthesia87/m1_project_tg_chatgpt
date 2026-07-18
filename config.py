import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-5.4-nano')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '4096'))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 1.0))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    REASONING_EFFORT = os.getenv('REASONING_EFFORT', 'medium').lower()


config = Config()

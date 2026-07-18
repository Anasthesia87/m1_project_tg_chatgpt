import logging
from config import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL, logging.INFO))

logger = logging.getLogger(__name__)


def show_user_action(user: dict, action: str) -> None:
    logger.info("Пользователь %s (%s) запустил команду %s!", user.full_name, user.id, action)

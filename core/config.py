from pydantic_settings import BaseSettings
import logging
import sys


class Settings(BaseSettings):
    DATABASE_URL: str
    DB_ECHO: bool

    # Настройки JWT
    SECRET_KEY: str
    SECRET_ALGORITHM: str
    TOKEN_EXPIRE_MINUTES: int

    # Настройки почты
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    
    # Базовый URL приложения
    HOST: str = "192.168.1.52"
    PORT: int = 8000
    BASE_URL: str = f"http://{HOST}:{PORT}/api/v1"
    STATIC_URL: str = f"http://{HOST}:{PORT}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

import logging
import sys

def setup_logging():
    """
    Настройка логирования для приложения.
    """
    # Создаем форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Создаем обработчик для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # Настраиваем логгеры для наших модулей
    loggers = [
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        # Убираем дублирование логов
        logger.propagate = False
        logger.addHandler(console_handler) 
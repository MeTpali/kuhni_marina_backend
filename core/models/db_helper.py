from typing import AsyncGenerator
from asyncio import current_task
import logging

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy import text

from core.config import settings

logger = logging.getLogger(__name__)

class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        # Определяем, нужен ли SSL (для локальной БД не нужен)
        connect_args = {
            "command_timeout": 60,  # 60 second timeout
            "server_settings": {
                "search_path": "kuhni_marina,public"  # Устанавливаем схему по умолчанию
            }
        }
        
        # Если URL содержит SSL параметры, добавляем SSL в connect_args
        if "sslmode=require" in url or "ssl=require" in url:
            connect_args["ssl"] = "require"
        
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,  # Enable connection testing
            connect_args=connect_args,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        session = self.session_factory()
        try:
            # Устанавливаем search_path для схемы kuhni_marina
            await session.execute(text("SET search_path TO kuhni_marina, public"))
            # Test the connection
            await session.execute(text("SELECT 1"))
            yield session
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            await session.close()
            raise
        finally:
            await session.close()


db_helper = DatabaseHelper(
    url=settings.DATABASE_URL,
    echo=settings.DB_ECHO,
)

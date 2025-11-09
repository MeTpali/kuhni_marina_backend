from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.db_helper import db_helper

async_session = db_helper.session_factory

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    from sqlalchemy import text
    async with async_session() as session:
        try:
            # Устанавливаем search_path для схемы kuhni_marina
            await session.execute(text("SET search_path TO kuhni_marina, public"))
            yield session
        finally:
            await session.close() 
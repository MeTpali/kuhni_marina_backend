"""
Общие хелперы для админки (сессии БД и т.д.).
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.db_helper import db_helper


async def with_image_session(coro):
    """
    Выполнить корутину с сессией БД (product/project images).
    coro(session) — асинхронная функция, принимающая AsyncSession.
    """
    async with db_helper.session_factory() as session:
        await session.execute(text("SET search_path TO kuhni_marina, public"))
        return await coro(session)

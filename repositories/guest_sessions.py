from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.guest_sessions import GuestSession


class GuestSessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self) -> GuestSession:
        now = datetime.now(timezone.utc)
        row = GuestSession(
            created_at=now,
            updated_at=now,
            last_seen_at=now,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def get_by_id(self, session_id: UUID) -> Optional[GuestSession]:
        result = await self.session.execute(
            select(GuestSession).where(GuestSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def touch(self, session_id: UUID) -> Optional[GuestSession]:
        row = await self.get_by_id(session_id)
        if row is None:
            return None
        now = datetime.now(timezone.utc)
        row.last_seen_at = now
        row.updated_at = now
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def count_stale_before(self, cutoff: datetime) -> int:
        """Количество сессий с last_seen_at строго раньше cutoff (для --dry-run)."""
        result = await self.session.execute(
            select(func.count())
            .select_from(GuestSession)
            .where(GuestSession.last_seen_at < cutoff)
        )
        return int(result.scalar() or 0)

    async def delete_stale_batch(self, cutoff: datetime, batch_size: int) -> int:
        """
        Удалить до batch_size сессий с last_seen_at < cutoff.
        Связанные guest_session_favorites удаляются по ON DELETE CASCADE.
        """
        ids_subq = (
            select(GuestSession.id)
            .where(GuestSession.last_seen_at < cutoff)
            .limit(batch_size)
        )
        stmt = delete(GuestSession).where(GuestSession.id.in_(ids_subq))
        result = await self.session.execute(stmt)
        await self.session.commit()
        return int(result.rowcount or 0)

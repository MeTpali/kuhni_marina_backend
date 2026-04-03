from datetime import datetime, timezone
from typing import List, Set, Tuple
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.guest_session_favorites import GuestSessionFavorite


class GuestSessionFavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_favorite_product_ids_among(
        self, session_id: UUID, product_ids: List[int]
    ) -> Set[int]:
        if not product_ids:
            return set()
        result = await self.session.execute(
            select(GuestSessionFavorite.product_id).where(
                GuestSessionFavorite.session_id == session_id,
                GuestSessionFavorite.product_id.in_(product_ids),
            )
        )
        return set(result.scalars().all())

    async def get_paginated_favorite_product_ids(
        self, session_id: UUID, page: int, page_size: int
    ) -> Tuple[List[int], int]:
        count_q = await self.session.execute(
            select(func.count())
            .select_from(GuestSessionFavorite)
            .where(GuestSessionFavorite.session_id == session_id)
        )
        total = int(count_q.scalar() or 0)
        if total == 0:
            return [], 0
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(GuestSessionFavorite.product_id)
            .where(GuestSessionFavorite.session_id == session_id)
            .order_by(GuestSessionFavorite.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def add_if_absent(self, session_id: UUID, product_id: int) -> bool:
        """Добавить в избранное. True — добавлено, False — уже было."""
        if await self.exists(session_id, product_id):
            return False
        row = GuestSessionFavorite(
            session_id=session_id,
            product_id=product_id,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(row)
        await self.session.commit()
        return True

    async def remove(self, session_id: UUID, product_id: int) -> int:
        result = await self.session.execute(
            delete(GuestSessionFavorite).where(
                GuestSessionFavorite.session_id == session_id,
                GuestSessionFavorite.product_id == product_id,
            )
        )
        await self.session.commit()
        return result.rowcount or 0

    async def exists(self, session_id: UUID, product_id: int) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(GuestSessionFavorite)
            .where(
                GuestSessionFavorite.session_id == session_id,
                GuestSessionFavorite.product_id == product_id,
            )
        )
        return (result.scalar() or 0) > 0

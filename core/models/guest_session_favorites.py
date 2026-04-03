from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class GuestSessionFavorite(Base):
    """Избранный товар гостевой сессии."""

    __tablename__ = "guest_session_favorites"

    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("guest_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (PrimaryKeyConstraint("session_id", "product_id"),)

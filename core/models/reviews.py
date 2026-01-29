from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base


# 7. Модель Review
class Review(Base):
    __tablename__ = "reviews"

    # ID отзыва
    id = Column(Integer, primary_key=True, index=True)
    # Отзыв к товару (опциональный)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    # Автор (опциональный)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # Имя автора
    author_name = Column(String, nullable=False)
    # Оценка (1–5)
    rating = Column(Integer, nullable=False)
    # Текст отзыва
    text = Column(Text, nullable=False)
    # Дата публикации
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    # Одобрен ли модератором
    is_approved = Column(Boolean, default=False, nullable=False)

    # Связи
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")


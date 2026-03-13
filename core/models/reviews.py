from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from .base import Base


class ReviewStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"


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
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    # Статус модерации
    status = Column(
        Enum(ReviewStatus, name="review_status", create_type=False, native_enum=True),
        default=ReviewStatus.PENDING,
        nullable=False,
    )

    # Связи
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def __repr__(self):
        return f"{self.id} - {self.author_name} ({self.rating}★)"

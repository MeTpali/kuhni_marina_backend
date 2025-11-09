from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from .base import Base


class CategoryType(str, enum.Enum):
    KITCHEN = "kitchen"
    FURNITURE = "furniture"


# 2. Модель Category
class Category(Base):
    __tablename__ = "categories"

    # ID категории
    id = Column(Integer, primary_key=True, index=True)
    # Название
    name = Column(String, nullable=False)
    # URL-идентификатор
    slug = Column(String, nullable=False, unique=True)
    # Родительская категория
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    # Тип категории (kitchen, furniture)
    type = Column(Enum(CategoryType), nullable=False)
    # Дата создания
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Связи
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")


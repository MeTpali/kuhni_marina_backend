from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base


class CategoryType(str, enum.Enum):
    KITCHEN = "KITCHEN"
    FURNITURE = "FURNITURE"


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
    # SQLAlchemy автоматически использует .value для Enum
    type = Column(Enum(CategoryType, name="category_type", create_type=False, native_enum=True), nullable=False)
    # Дата создания
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    # Признак активности
    is_active = Column(Boolean, default=True, nullable=False)

    # Связи
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", foreign_keys=[parent_id])
    products = relationship("Product", back_populates="category")


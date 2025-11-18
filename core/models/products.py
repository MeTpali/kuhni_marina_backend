from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Boolean,
    Enum,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from .base import Base


class ProductType(str, enum.Enum):
    KITCHEN = "KITCHEN"
    FURNITURE = "FURNITURE"


# 3. Модель Product
class Product(Base):
    __tablename__ = "products"

    # ID товара
    id = Column(Integer, primary_key=True, index=True)
    # Категория
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    # Название
    name = Column(String, nullable=False)
    # SEO-slug
    slug = Column(String, nullable=False, unique=True)
    # Описание
    description = Column(Text, nullable=True)
    # Цена
    price = Column(Numeric(10, 2), nullable=True)
    # Новинка
    is_new = Column(Boolean, default=False, nullable=False)
    # Хит продаж
    is_hit = Column(Boolean, default=False, nullable=False)
    # Тип (kitchen, furniture)
    type = Column(Enum(ProductType, name="category_type", create_type=False), nullable=False)
    # Дата создания
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    # Дата обновления
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    # Связи
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product")
    projects = relationship("ProjectProduct", back_populates="product")


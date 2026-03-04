from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Boolean,
    Enum,
    Index,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base
from .products import ProductType


class DiscountType(str, enum.Enum):
    PERCENTAGE = "PERCENTAGE"  # Процентная скидка
    FIXED = "FIXED"            # Фиксированная сумма


class DiscountScope(str, enum.Enum):
    PRODUCT = "PRODUCT"        # На конкретный продукт
    CATEGORY = "CATEGORY"      # На категорию
    TYPE = "TYPE"              # На тип продукта (KITCHEN/FURNITURE)
    ALL = "ALL"                # На все продукты


# Модель Discount
class Discount(Base):
    __tablename__ = "discounts"

    # ID скидки
    id = Column(Integer, primary_key=True, index=True)
    # Название акции
    name = Column(String, nullable=False)
    # Тип скидки (процентная или фиксированная)
    discount_type = Column(Enum(DiscountType, name="discount_type", create_type=False, native_enum=True), nullable=False)
    # Значение скидки (процент или сумма)
    value = Column(Numeric(10, 2), nullable=False)
    # Область применения
    scope = Column(Enum(DiscountScope, name="discount_scope", create_type=False, native_enum=True), nullable=False)
    
    # Привязки (nullable в зависимости от scope)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    product_type = Column(Enum(ProductType, name="category_type", create_type=False, native_enum=True), nullable=True)
    
    # Временные рамки
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    # Признак активности
    is_active = Column(Boolean, default=True, nullable=False)
    # Приоритет при наложении скидок (чем больше, тем выше приоритет)
    priority = Column(Integer, default=0, nullable=False)
    
    # Дата создания
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    # Дата обновления
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    # Связи
    product = relationship("Product", back_populates="discounts")
    category = relationship("Category", back_populates="discounts")

    # Индексы для оптимизации запросов
    __table_args__ = (
        Index('idx_discount_dates', 'start_date', 'end_date'),
        Index('idx_discount_active', 'is_active'),
        Index('idx_discount_scope', 'scope'),
    )

    def __repr__(self):
        return f"{self.id} - {self.name} ({self.value}%)"

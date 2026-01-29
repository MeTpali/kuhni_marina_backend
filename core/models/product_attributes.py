from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from .base import Base


# 6. Модель ProductAttribute
class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    # ID товара
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    # ID характеристики
    attribute_id = Column(Integer, ForeignKey("attributes.id"), primary_key=True)
    # Значение
    value = Column(String, nullable=False)

    # Связи
    product = relationship("Product", back_populates="attributes")
    attribute = relationship("Attribute", back_populates="product_attributes")


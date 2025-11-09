from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from .base import Base


# 5. Модель Attribute
class Attribute(Base):
    __tablename__ = "attributes"

    # ID характеристики
    id = Column(Integer, primary_key=True, index=True)
    # Название характеристики
    name = Column(String, nullable=False)
    # Единица измерения
    unit = Column(String, nullable=True)

    # Связи
    product_attributes = relationship("ProductAttribute", back_populates="attribute")


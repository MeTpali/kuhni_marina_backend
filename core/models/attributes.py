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

    def __repr__(self):
        unit_str = f" ({self.unit})" if self.unit else ""
        return f"{self.id} - {self.name}{unit_str}"

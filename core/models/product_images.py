from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from .base import Base


# 4. Модель ProductImage
class ProductImage(Base):
    __tablename__ = "product_images"

    # ID изображения
    id = Column(Integer, primary_key=True, index=True)
    # Товар
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    # Ссылка на изображение
    image_url = Column(String, nullable=False)
    # Главное изображение
    is_main = Column(Boolean, default=False, nullable=False)

    # Связи
    product = relationship("Product", back_populates="images")


from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from .base import Base


# 10. Модель ProjectProduct
class ProjectProduct(Base):
    __tablename__ = "project_products"

    # Проект
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    # Использованный товар
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)

    # Связи
    project = relationship("Project", back_populates="products")
    product = relationship("Product", back_populates="projects")


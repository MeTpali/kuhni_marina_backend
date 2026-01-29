from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base


# 8. Модель Project
class Project(Base):
    __tablename__ = "projects"

    # ID проекта
    id = Column(Integer, primary_key=True, index=True)
    # Название
    name = Column(String, nullable=False)
    # Описание
    description = Column(Text, nullable=True)
    # Адрес или район
    location = Column(String, nullable=True)
    # Дата добавления
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Связи
    images = relationship("ProjectImage", back_populates="project", cascade="all, delete-orphan")
    products = relationship("ProjectProduct", back_populates="project", cascade="all, delete-orphan")


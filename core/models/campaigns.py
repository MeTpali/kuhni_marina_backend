from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


# Модель Campaign (маркетинговая акция)
class Campaign(Base):
    __tablename__ = "campaigns"

    # ID акции
    id = Column(Integer, primary_key=True, index=True)
    # Название
    name = Column(String, nullable=False)
    # SEO-slug
    slug = Column(String, nullable=False, unique=True)
    # Описание
    description = Column(Text, nullable=True)
    # Изображение акции
    banner_image_url = Column(String, nullable=True)
    # Ссылка на лендинг акции
    landing_url = Column(String, nullable=True)
    # Короткий бейдж ("-20%", "Ликвидация")
    badge_text = Column(String, nullable=True)
    # Временные рамки
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    # Активна ли акция
    is_active = Column(Boolean, default=True, nullable=False)
    # Приоритет кампании
    priority = Column(Integer, default=0, nullable=False)
    # Дата создания
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    # Дата обновления
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    # Связи
    discounts = relationship("Discount", back_populates="campaign")

    def __repr__(self):
        return f"{self.id} - {self.name}"

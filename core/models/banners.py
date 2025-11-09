from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
)
from .base import Base


# 12. Модель Banner
class Banner(Base):
    __tablename__ = "banners"

    # ID баннера
    id = Column(Integer, primary_key=True, index=True)
    # Заголовок
    title = Column(String, nullable=False)
    # Изображение
    image_url = Column(String, nullable=False)
    # Ссылка
    link_url = Column(String, nullable=True)
    # Порядок вывода
    position = Column(Integer, default=0, nullable=False)
    # Активен ли баннер
    is_active = Column(Boolean, default=True, nullable=False)


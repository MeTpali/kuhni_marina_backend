from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from .base import Base


# 9. Модель ProjectImage
class ProjectImage(Base):
    __tablename__ = "project_images"

    # ID изображения
    id = Column(Integer, primary_key=True, index=True)
    # Проект
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    # Ссылка на изображение
    image_url = Column(String, nullable=False)
    # Главное фото
    is_main = Column(Boolean, default=False, nullable=False)

    # Связи
    project = relationship("Project", back_populates="images")


from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
)
from .base import Base


class BackgroundImage(Base):
    __tablename__ = "background_images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

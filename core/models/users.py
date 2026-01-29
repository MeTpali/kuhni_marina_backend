from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    Enum,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from .base import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    CUSTOMER = "CUSTOMER"


# 1. Модель User
class User(Base):
    __tablename__ = "users"

    # id пользователя обязательный
    id = Column(Integer, primary_key=True, index=True)
    # Полное имя
    full_name = Column(Text, nullable=True)
    # Телефон
    phone = Column(Text, nullable=True)
    # Почта уникальная
    email = Column(String, unique=True, nullable=True)
    # Hash пароля обязательный
    password_hash = Column(Text, nullable=False)
    # Роль пользователя (admin, manager, customer)
    role = Column(Enum(UserRole, name="user_role", create_type=False), nullable=False)
    # Время создания обязательный
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    # Время обновления
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    # Связи
    reviews = relationship("Review", back_populates="user")
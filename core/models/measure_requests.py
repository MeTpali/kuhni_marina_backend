from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    ForeignKey,
    Enum,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from .base import Base


class MeasureRequestStatus(str, enum.Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


# 11. Модель MeasureRequest
class MeasureRequest(Base):
    __tablename__ = "measure_requests"

    # ID заявки
    id = Column(Integer, primary_key=True, index=True)
    # Имя клиента
    full_name = Column(String, nullable=False)
    # Телефон
    phone = Column(String, nullable=False)
    # Адрес
    address = Column(String, nullable=False)
    # Предпочтительная дата
    preferred_date = Column(Date, nullable=True)
    # Комментарий
    comment = Column(Text, nullable=True)
    # Статус заявки
    status = Column(Enum(MeasureRequestStatus, name="measure_request_status", create_type=False), default=MeasureRequestStatus.NEW, nullable=False)
    # Дата создания
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


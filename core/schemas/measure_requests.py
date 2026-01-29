from typing import List, Optional
from datetime import date, datetime

from .base import BaseSchema
from core.models.measure_requests import MeasureRequestStatus


class MeasureRequestBase(BaseSchema):
    full_name: str
    phone: str
    address: str
    preferred_date: Optional[date] = None
    comment: Optional[str] = None
    status: Optional[MeasureRequestStatus] = None


class MeasureRequestCreateRequest(MeasureRequestBase):
    pass


class MeasureRequestUpdateRequest(BaseSchema):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    preferred_date: Optional[date] = None
    comment: Optional[str] = None
    status: Optional[MeasureRequestStatus] = None


class MeasureRequestStatusUpdateRequest(BaseSchema):
    status: MeasureRequestStatus


class MeasureRequestResponse(MeasureRequestBase):
    id: int
    status: MeasureRequestStatus
    created_at: datetime
    message: Optional[str] = None


class MeasureRequestListResponse(BaseSchema):
    items: List[MeasureRequestResponse]
    message: Optional[str] = None


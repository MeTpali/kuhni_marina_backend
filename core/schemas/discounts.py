from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from core.models.discounts import DiscountType, DiscountScope
from core.models.products import ProductType
from .base import BaseSchema


class DiscountBase(BaseSchema):
    name: str
    discount_type: DiscountType
    value: Decimal
    scope: DiscountScope
    campaign_id: Optional[int] = None
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    product_type: Optional[ProductType] = None
    start_date: datetime
    end_date: datetime
    priority: int = 0


class DiscountCreateRequest(DiscountBase):
    is_active: bool = True


class DiscountUpdateRequest(BaseSchema):
    name: Optional[str] = None
    discount_type: Optional[DiscountType] = None
    value: Optional[Decimal] = None
    scope: Optional[DiscountScope] = None
    campaign_id: Optional[int] = None
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    product_type: Optional[ProductType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class DiscountCampaignInfo(BaseSchema):
    id: int
    name: str
    slug: str
    badge_text: Optional[str] = None
    landing_url: Optional[str] = None


class DiscountResponse(DiscountBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    campaign: Optional[DiscountCampaignInfo] = None
    message: Optional[str] = None


class DiscountListResponse(BaseSchema):
    items: List[DiscountResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    message: Optional[str] = None


class DiscountDeleteResponse(BaseSchema):
    discount_id: int
    message: Optional[str] = None

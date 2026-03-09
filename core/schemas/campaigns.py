from typing import List, Optional
from datetime import datetime

from .base import BaseSchema


class CampaignBase(BaseSchema):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    banner_image_url: Optional[str] = None
    landing_url: Optional[str] = None
    badge_text: Optional[str] = None
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    priority: int = 0


class CampaignCreateRequest(CampaignBase):
    pass


class CampaignUpdateRequest(BaseSchema):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    banner_image_url: Optional[str] = None
    landing_url: Optional[str] = None
    badge_text: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class CampaignResponse(CampaignBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    message: Optional[str] = None


class CampaignListResponse(BaseSchema):
    items: List[CampaignResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    message: Optional[str] = None


class CampaignDeleteResponse(BaseSchema):
    campaign_id: int
    message: Optional[str] = None

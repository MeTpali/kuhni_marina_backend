from typing import List

from .base import BaseSchema


class BannerBase(BaseSchema):
    title: str
    image_url: str
    link_url: str | None = None
    position: int = 0
    is_active: bool | None = True


class BannerCreateRequest(BannerBase):
    pass


class BannerResponse(BannerBase):
    id: int
    message: str | None = None


class BannerListResponse(BaseSchema):
    items: List[BannerResponse]
    message: str | None = None


class BannerDeleteResponse(BaseSchema):
    banner_id: int
    message: str | None = None


from typing import List

from .base import BaseSchema


class BackgroundImageBase(BaseSchema):
    url: str
    is_active: bool | None = True


class BackgroundImageCreateRequest(BackgroundImageBase):
    pass


class BackgroundImageUpdateRequest(BackgroundImageBase):
    pass


class BackgroundImageResponse(BackgroundImageBase):
    id: int
    message: str | None = None


class BackgroundImageListResponse(BaseSchema):
    items: List[BackgroundImageResponse]
    message: str | None = None


class BackgroundImageDeleteResponse(BaseSchema):
    background_image_id: int
    message: str | None = None

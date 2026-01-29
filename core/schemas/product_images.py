from typing import List

from .base import BaseSchema


class ProductImageBase(BaseSchema):
    product_id: int
    image_url: str
    is_main: bool | None = False


class ProductImageCreateRequest(ProductImageBase):
    pass


class ProductImageResponse(ProductImageBase):
    id: int
    message: str | None = None


class ProductImageListResponse(BaseSchema):
    items: List[ProductImageResponse]
    message: str | None = None


class ProductImageDeleteResponse(BaseSchema):
    product_image_id: int
    message: str | None = None


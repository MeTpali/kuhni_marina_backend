from typing import List

from .base import BaseSchema


class ProductAttributeBase(BaseSchema):
    product_id: int
    attribute_id: int
    value: str


class ProductAttributeCreateRequest(ProductAttributeBase):
    pass


class ProductAttributeUpdateRequest(BaseSchema):
    value: str


class ProductAttributeResponse(ProductAttributeBase):
    message: str | None = None


class ProductAttributeListResponse(BaseSchema):
    items: List[ProductAttributeResponse]
    message: str | None = None


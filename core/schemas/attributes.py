from typing import List

from .base import BaseSchema


class AttributeBase(BaseSchema):
    name: str
    unit: str | None = None


class AttributeCreateRequest(AttributeBase):
    pass


class AttributeUpdateRequest(AttributeBase):
    pass


class AttributeResponse(AttributeBase):
    id: int
    message: str | None = None


class AttributeListResponse(BaseSchema):
    items: List[AttributeResponse]
    message: str | None = None


class AttributeDeleteResponse(BaseSchema):
    attribute_id: int
    message: str | None = None


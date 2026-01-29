from typing import List

from .base import BaseSchema


class ProjectProductBase(BaseSchema):
    project_id: int
    product_id: int


class ProjectProductCreateRequest(ProjectProductBase):
    pass


class ProjectProductResponse(ProjectProductBase):
    message: str | None = None


class ProjectProductListResponse(BaseSchema):
    items: List[ProjectProductResponse]
    message: str | None = None


class ProjectProductDeleteResponse(ProjectProductBase):
    message: str | None = None


class ProjectIdsByProductResponse(BaseSchema):
    product_id: int
    project_ids: List[int]
    message: str | None = None


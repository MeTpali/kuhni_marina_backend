from typing import List, Optional

from pydantic import Field

from core.models.categories import CategoryType
from .base import BaseSchema


class CategoryBase(BaseSchema):
    name: str
    slug: str
    parent_id: Optional[int] = None
    type: CategoryType


class CategoryCreateRequest(BaseSchema):
    name: str
    slug: Optional[str] = None
    parent_id: Optional[int] = None
    type: CategoryType
    is_active: bool = True


class CategoryResponse(CategoryBase):
    id: int
    is_active: bool = True
    message: Optional[str] = None


class CategoryTreeNode(CategoryResponse):
    children: List["CategoryTreeNode"] = Field(default_factory=list)


class CategoryListResponse(BaseSchema):
    items: List[CategoryTreeNode]
    message: Optional[str] = None


class CategoryDeleteResponse(BaseSchema):
    category_id: int
    message: Optional[str] = None


# Forward references resolution
CategoryTreeNode.model_rebuild()


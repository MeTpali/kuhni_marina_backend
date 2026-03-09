from typing import List, Optional
from datetime import datetime

from .base import BaseSchema
from .project_images import ProjectImageResponse


class ProjectBase(BaseSchema):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None


class ProjectCreateRequest(ProjectBase):
    pass


class ProjectUpdateRequest(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    message: Optional[str] = None


class ProjectDetailResponse(ProjectBase):
    id: int
    created_at: datetime
    images: List[ProjectImageResponse]
    product_ids: List[int]
    message: Optional[str] = None


class ProjectListResponse(BaseSchema):
    items: List[ProjectResponse]
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None
    message: Optional[str] = None


class ProjectDeleteResponse(BaseSchema):
    project_id: int
    message: Optional[str] = None


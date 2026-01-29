from typing import List

from .base import BaseSchema


class ProjectImageBase(BaseSchema):
    project_id: int
    image_url: str
    is_main: bool | None = False


class ProjectImageCreateRequest(ProjectImageBase):
    pass


class ProjectImageCreateBulkRequest(BaseSchema):
    images: List[ProjectImageCreateRequest]


class ProjectImageResponse(ProjectImageBase):
    id: int
    message: str | None = None


class ProjectImageListResponse(BaseSchema):
    items: List[ProjectImageResponse]
    message: str | None = None


class ProjectImageDeleteResponse(BaseSchema):
    project_image_id: int
    message: str | None = None


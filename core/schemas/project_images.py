from typing import List, Optional

from .base import BaseSchema


class ProjectImagesSetRequest(BaseSchema):
    """Запрос на установку списка изображений проекта (замена существующих)."""
    project_id: int
    image_urls: List[str]
    main_index: Optional[int] = None  # порядковый номер (1-based); если не задан или некорректен — главным будет первое


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


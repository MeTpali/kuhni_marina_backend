from typing import List, Optional

from .base import BaseSchema


class ProductImagesSetRequest(BaseSchema):
    """Запрос на установку списка изображений продукта (замена существующих)."""
    product_id: int
    image_urls: List[str]
    main_index: Optional[int] = None  # порядковый номер (1-based); если не задан или некорректен — главным будет первое


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


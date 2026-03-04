from typing import List, Optional
from decimal import Decimal

from pydantic import Field

from core.models.products import ProductType
from core.schemas.categories import CategoryResponse
from .base import BaseSchema


# Вложенные схемы для атрибутов и изображений
class ProductAttributeResponse(BaseSchema):
    attribute_id: int
    attribute_name: str
    attribute_unit: Optional[str] = None
    value: str


class ProductImageResponse(BaseSchema):
    id: int
    image_url: str
    is_main: bool


class ProductDiscountInfo(BaseSchema):
    """Информация о скидке на продукт"""
    discount_percent: Optional[Decimal] = None  # Процент скидки
    discount_amount: Optional[Decimal] = None   # Величина скидки в деньгах
    final_price: Optional[Decimal] = None       # Итоговая цена с учетом скидки


# Базовые схемы продукта
class ProductBase(BaseSchema):
    name: str
    slug: Optional[str] = None
    category_id: int
    description: Optional[str] = None
    price: Optional[Decimal] = None
    is_new: bool = False
    is_hit: bool = False
    type: ProductType


class ProductCreateRequest(ProductBase):
    attributes: List[dict] = Field(default_factory=list)  # [{"attribute_id": int, "value": str}]
    images: List[dict] = Field(default_factory=list)  # [{"image_url": str, "is_main": bool}]


class ProductUpdateRequest(BaseSchema):
    name: Optional[str] = None
    slug: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    is_new: Optional[bool] = None
    is_hit: Optional[bool] = None
    type: Optional[ProductType] = None
    attributes: Optional[List[dict]] = None
    images: Optional[List[dict]] = None


class ProductResponse(ProductBase):
    id: int
    category: CategoryResponse
    attributes: List[ProductAttributeResponse] = Field(default_factory=list)
    images: List[ProductImageResponse] = Field(default_factory=list)
    is_active: bool = True
    created_at: str
    updated_at: Optional[str] = None
    message: Optional[str] = None
    discount: Optional[ProductDiscountInfo] = None


class ProductListItemResponse(BaseSchema):
    id: int
    name: str
    slug: str
    category_id: int
    category_name: Optional[str] = None
    price: Optional[Decimal] = None
    is_new: bool = False
    is_hit: bool = False
    type: ProductType
    main_image: Optional[str] = None
    is_active: bool = True
    discount: Optional[ProductDiscountInfo] = None


class ProductCatalogResponse(BaseSchema):
    items: List[ProductListItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    message: Optional[str] = None


class ProductIdListResponse(BaseSchema):
    product_ids: List[int]
    total: int
    message: Optional[str] = None


class ProductListResponse(BaseSchema):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    message: Optional[str] = None


class ProductDeleteResponse(BaseSchema):
    product_id: int
    message: Optional[str] = None

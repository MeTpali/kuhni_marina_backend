from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from api.deps import get_product_service
from services.products import ProductService
from core.schemas.products import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductCatalogResponse,
    ProductIdListResponse,
    ProductDeleteResponse,
)

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Product not found"}},
)


@router.get(
    "/catalog",
    response_model=ProductCatalogResponse,
    summary="Получить каталог продуктов",
    description="Возвращает каталог продуктов с фильтрами и пагинацией",
)
async def get_product_catalog(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    category_ids: Optional[List[int]] = Query(None, description="Фильтр по ID категорий"),
    attribute_filters: Optional[str] = Query(
        None, description='Фильтр по атрибутам в формате JSON: [{"attribute_id": 1, "value": "значение"}]'
    ),
    product_service: ProductService = Depends(get_product_service),
):
    """
    Получить каталог продуктов:
    - Поддерживает фильтрацию по категориям и атрибутам
    - Поддерживает пагинацию
    - Возвращает краткую информацию о продуктах
    """
    import json

    attr_filters = None
    if attribute_filters:
        try:
            attr_filters = json.loads(attribute_filters)
        except json.JSONDecodeError:
            attr_filters = None

    return await product_service.get_product_catalog(
        page=page,
        page_size=page_size,
        category_ids=category_ids,
        attribute_filters=attr_filters,
    )


@router.get(
    "/ids",
    response_model=ProductIdListResponse,
    summary="Получить список ID продуктов",
    description="Возвращает список ID продуктов с фильтрами",
)
async def get_product_ids(
    category_ids: Optional[List[int]] = Query(None, description="Фильтр по ID категорий"),
    attribute_filters: Optional[str] = Query(
        None, description='Фильтр по атрибутам в формате JSON: [{"attribute_id": 1, "value": "значение"}]'
    ),
    product_service: ProductService = Depends(get_product_service),
):
    """
    Получить список ID продуктов:
    - Поддерживает фильтрацию по категориям и атрибутам
    - Возвращает только ID продуктов
    """
    import json

    attr_filters = None
    if attribute_filters:
        try:
            attr_filters = json.loads(attribute_filters)
        except json.JSONDecodeError:
            attr_filters = None

    return await product_service.get_product_ids(
        category_ids=category_ids,
        attribute_filters=attr_filters,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Получить продукт по ID",
    description="Возвращает продукт с категорией, атрибутами и изображениями",
    responses={
        200: {"description": "Продукт найден"},
        404: {"description": "Продукт не найден"},
    },
)
async def get_product_by_id(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
):
    """
    Получить продукт по идентификатору:
    - Возвращает полную информацию о продукте
    - Включает категорию, атрибуты и изображения
    """
    return await product_service.get_product_by_id(product_id)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать продукт",
    description="Создает новый продукт",
    responses={
        201: {"description": "Продукт успешно создан"},
        400: {"description": "Некорректные данные"},
        404: {"description": "Категория не найдена"},
    },
)
async def create_product(
    request: ProductCreateRequest,
    product_service: ProductService = Depends(get_product_service),
):
    """
    Создать новый продукт:
    - Проверяет корректность данных
    - Создает продукт с изображениями и атрибутами
    - Автоматически генерирует slug, если не указан
    """
    return await product_service.create_product(request)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Обновить продукт",
    description="Обновляет продукт по идентификатору",
    responses={
        200: {"description": "Продукт успешно обновлен"},
        400: {"description": "Некорректные данные"},
        404: {"description": "Продукт не найден"},
    },
)
async def update_product(
    product_id: int,
    request: ProductUpdateRequest,
    product_service: ProductService = Depends(get_product_service),
):
    """
    Обновить продукт:
    - Обновляет указанные поля
    - Поддерживает обновление изображений и атрибутов
    """
    return await product_service.update_product(product_id, request)


@router.delete(
    "/{product_id}",
    response_model=ProductDeleteResponse,
    summary="Удалить продукт",
    description="Деактивирует продукт (мягкое удаление)",
    responses={
        200: {"description": "Продукт успешно деактивирован"},
        404: {"description": "Продукт не найден"},
    },
)
async def delete_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
):
    """
    Удалить продукт:
    - Деактивирует продукт (is_active = false)
    - Продукт не удаляется физически из базы данных
    """
    return await product_service.delete_product(product_id)

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from api.deps import get_product_service
from services.products import ProductService
from core.models.products import ProductType
from core.schemas.products import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductCatalogResponse,
    ProductIdListResponse,
    ProductSearchSuggestionsResponse,
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
    is_hit: Optional[bool] = Query(None, description="Фильтр по хитам продаж"),
    is_new: Optional[bool] = Query(None, description="Фильтр по новинкам"),
    has_discount: Optional[bool] = Query(None, description="Фильтр по наличию скидки"),
    campaign_id: Optional[int] = Query(None, description="Фильтр по ID акции"),
    type: Optional[ProductType] = Query(None, description="Фильтр по типу продукта (KITCHEN, FURNITURE)"),
    search: Optional[str] = Query(None, description="Поиск по названию и описанию"),
    product_service: ProductService = Depends(get_product_service),
):
    """
    Получить каталог продуктов:
    - Поддерживает фильтрацию по категориям, атрибутам, типу, хитам, новинкам и скидкам
    - Поддерживает поиск по тексту (название, описание)
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
        is_hit=is_hit,
        is_new=is_new,
        has_discount=has_discount,
        campaign_id=campaign_id,
        product_type=type,
        search_query=search,
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
    "/hits",
    response_model=ProductCatalogResponse,
    summary="Получить хиты продаж",
    description="Возвращает продукты-хиты с пагинацией",
)
async def get_product_hits(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    category_ids: Optional[List[int]] = Query(None, description="Фильтр по ID категорий"),
    attribute_filters: Optional[str] = Query(
        None, description='Фильтр по атрибутам в формате JSON: [{"attribute_id": 1, "value": "значение"}]'
    ),
    product_service: ProductService = Depends(get_product_service),
):
    """Получить каталог продуктов-хитов с пагинацией."""
    import json
    attr_filters = None
    if attribute_filters:
        try:
            attr_filters = json.loads(attribute_filters)
        except json.JSONDecodeError:
            attr_filters = None
    return await product_service.get_catalog_hits(
        page=page,
        page_size=page_size,
        category_ids=category_ids,
        attribute_filters=attr_filters,
    )


@router.get(
    "/new",
    response_model=ProductCatalogResponse,
    summary="Получить новинки",
    description="Возвращает новинки с пагинацией",
)
async def get_product_new(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    category_ids: Optional[List[int]] = Query(None, description="Фильтр по ID категорий"),
    attribute_filters: Optional[str] = Query(
        None, description='Фильтр по атрибутам в формате JSON: [{"attribute_id": 1, "value": "значение"}]'
    ),
    product_service: ProductService = Depends(get_product_service),
):
    """Получить каталог новинок с пагинацией."""
    import json
    attr_filters = None
    if attribute_filters:
        try:
            attr_filters = json.loads(attribute_filters)
        except json.JSONDecodeError:
            attr_filters = None
    return await product_service.get_catalog_new(
        page=page,
        page_size=page_size,
        category_ids=category_ids,
        attribute_filters=attr_filters,
    )


@router.get(
    "/discounts",
    response_model=ProductCatalogResponse,
    summary="Получить продукты со скидкой",
    description="Возвращает продукты с активной скидкой с пагинацией",
)
async def get_product_discounts(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    category_ids: Optional[List[int]] = Query(None, description="Фильтр по ID категорий"),
    attribute_filters: Optional[str] = Query(
        None, description='Фильтр по атрибутам в формате JSON: [{"attribute_id": 1, "value": "значение"}]'
    ),
    product_service: ProductService = Depends(get_product_service),
):
    """Получить каталог продуктов со скидкой с пагинацией."""
    import json
    attr_filters = None
    if attribute_filters:
        try:
            attr_filters = json.loads(attribute_filters)
        except json.JSONDecodeError:
            attr_filters = None
    return await product_service.get_catalog_discounts(
        page=page,
        page_size=page_size,
        category_ids=category_ids,
        attribute_filters=attr_filters,
    )


@router.get(
    "/search/suggestions",
    response_model=ProductSearchSuggestionsResponse,
    summary="Подсказки поиска",
    description="Быстрые подсказки для автодополнения: id, картинка, описание до 150 символов, цена, скидка",
)
async def get_search_suggestions(
    text: str = Query(..., description="Текст поиска"),
    type: Optional[ProductType] = Query(None, description="Фильтр по типу продукта (KITCHEN, FURNITURE)"),
    limit: int = Query(10, ge=1, le=50, description="Максимальное количество подсказок в выдаче"),
    product_service: ProductService = Depends(get_product_service),
):
    """
    Подсказки поиска для пользователя:
    - Текст поиска (обязательно), тип продукта (опционально), лимит (по умолчанию 10)
    - Каждый элемент: id, картинка (опционально), описание не более 150 символов с троеточием, цена, скидка (опционально)
    """
    return await product_service.get_search_suggestions(
        text=text,
        product_type=type,
        limit=limit,
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

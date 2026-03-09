from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from api.deps import get_discount_service
from services.discounts import DiscountService
from core.models.discounts import DiscountType, DiscountScope
from core.models.products import ProductType
from core.schemas.discounts import (
    DiscountCreateRequest,
    DiscountUpdateRequest,
    DiscountResponse,
    DiscountListResponse,
    DiscountDeleteResponse,
)

router = APIRouter(
    prefix="/discounts",
    tags=["discounts"],
    responses={404: {"description": "Discount not found"}},
)


@router.get(
    "",
    response_model=DiscountListResponse,
    summary="Получить список скидок",
    description="Возвращает список скидок с фильтрацией и сортировкой",
)
async def get_discounts(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    include_inactive: bool = Query(False, description="Включить неактивные скидки"),
    scope: Optional[DiscountScope] = Query(None, description="Фильтр по области применения"),
    discount_type: Optional[DiscountType] = Query(None, description="Фильтр по типу скидки"),
    campaign_id: Optional[int] = Query(None, description="Фильтр по ID акции"),
    product_id: Optional[int] = Query(None, description="Фильтр по ID продукта"),
    category_id: Optional[int] = Query(None, description="Фильтр по ID категории"),
    product_type: Optional[ProductType] = Query(None, description="Фильтр по типу продукта"),
    is_active: Optional[bool] = Query(None, description="Фильтр по активности"),
    sort_by: Optional[str] = Query(
        None,
        description="Поле для сортировки (name, created_at, priority, start_date, end_date)",
    ),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Порядок сортировки (asc/desc)"),
    discount_service: DiscountService = Depends(get_discount_service),
):
    """
    Получить список скидок с фильтрацией и сортировкой:
    - Поддерживает пагинацию
    - Фильтрация по области применения, типу, продукту, категории, типу продукта
    - Сортировка по различным полям
    """
    return await discount_service.get_discounts(
        page=page,
        page_size=page_size,
        include_inactive=include_inactive,
        scope=scope,
        discount_type=discount_type,
        campaign_id=campaign_id,
        product_id=product_id,
        category_id=category_id,
        product_type=product_type,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/{discount_id}",
    response_model=DiscountResponse,
    summary="Получить скидку по идентификатору",
    description="Возвращает скидку с указанным идентификатором",
    responses={
        200: {"description": "Скидка найдена"},
        404: {"description": "Скидка не найдена"},
    },
)
async def get_discount_by_id(
    discount_id: int,
    discount_service: DiscountService = Depends(get_discount_service),
):
    """
    Получить скидку по идентификатору:
    - Возвращает скидку, если она существует и активна
    - Возвращает ошибку 404, если скидка не найдена
    """
    return await discount_service.get_discount_by_id(discount_id)


@router.post(
    "",
    response_model=DiscountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать скидку",
    description="Создает и возвращает новую скидку",
    responses={
        201: {"description": "Скидка успешно создана"},
        400: {"description": "Некорректные данные для скидки"},
    },
)
async def create_discount(
    request: DiscountCreateRequest,
    discount_service: DiscountService = Depends(get_discount_service),
):
    """
    Создать новую скидку:
    - Проверяет корректность данных
    - Валидирует соответствие scope и привязок
    - Создает и возвращает созданную скидку
    """
    return await discount_service.create_discount(request)


@router.put(
    "/{discount_id}",
    response_model=DiscountResponse,
    summary="Обновить скидку",
    description="Обновляет скидку по идентификатору",
    responses={
        200: {"description": "Скидка успешно обновлена"},
        400: {"description": "Некорректные данные для скидки"},
        404: {"description": "Скидка не найдена"},
    },
)
async def update_discount(
    discount_id: int,
    request: DiscountUpdateRequest,
    discount_service: DiscountService = Depends(get_discount_service),
):
    """
    Обновить скидку:
    - Проверяет корректность данных
    - Валидирует соответствие scope и привязок
    - Обновляет и возвращает обновленную скидку
    """
    return await discount_service.update_discount(discount_id, request)


@router.delete(
    "/{discount_id}",
    response_model=DiscountDeleteResponse,
    summary="Удалить скидку",
    description="Удаляет скидку по идентификатору (деактивирует)",
    responses={
        200: {"description": "Скидка успешно удалена"},
        404: {"description": "Скидка не найдена"},
    },
)
async def delete_discount(
    discount_id: int,
    discount_service: DiscountService = Depends(get_discount_service),
):
    """
    Удалить скидку:
    - Деактивирует скидку (устанавливает is_active=False)
    - Скидка не удаляется физически из базы данных
    """
    return await discount_service.delete_discount(discount_id)

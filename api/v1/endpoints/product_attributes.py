from fastapi import APIRouter, Depends, status

from api.deps import get_product_attribute_service
from services.product_attributes import ProductAttributeService
from core.schemas.product_attributes import (
    ProductAttributeCreateRequest,
    ProductAttributeUpdateRequest,
    ProductAttributeResponse,
    ProductAttributeListResponse,
)

router = APIRouter(
    prefix="/product-attributes",
    tags=["product-attributes"],
    responses={404: {"description": "Product attribute not found"}},
)


@router.get(
    "",
    response_model=ProductAttributeListResponse,
    summary="Получить все атрибуты продуктов",
    description="Возвращает список всех атрибутов продуктов",
)
async def get_product_attributes(
    product_attribute_service: ProductAttributeService = Depends(get_product_attribute_service),
):
    """
    Получить список всех атрибутов продуктов:
    - Возвращает все существующие атрибуты продуктов
    - Отсортированы по product_id и attribute_id
    """
    return await product_attribute_service.get_all_product_attributes()


@router.get(
    "/{product_id}/{attribute_id}",
    response_model=ProductAttributeResponse,
    summary="Получить атрибут продукта по идентификаторам",
    description="Возвращает атрибут продукта с указанными идентификаторами продукта и атрибута",
    responses={
        200: {"description": "Атрибут продукта найден"},
        404: {"description": "Атрибут продукта не найден"},
    },
)
async def get_product_attribute_by_id(
    product_id: int,
    attribute_id: int,
    product_attribute_service: ProductAttributeService = Depends(get_product_attribute_service),
):
    """
    Получить атрибут продукта по идентификаторам:
    - Возвращает атрибут продукта, если он существует
    - Возвращает ошибку 404, если атрибут продукта не найден
    """
    return await product_attribute_service.get_product_attribute_by_id(product_id, attribute_id)


@router.post(
    "",
    response_model=ProductAttributeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать атрибут продукта",
    description="Создает и возвращает новый атрибут продукта",
    responses={
        201: {"description": "Атрибут продукта успешно создан"},
        400: {"description": "Некорректные данные для атрибута продукта"},
    },
)
async def create_product_attribute(
    request: ProductAttributeCreateRequest,
    product_attribute_service: ProductAttributeService = Depends(get_product_attribute_service),
):
    """
    Создать новый атрибут продукта:
    - Проверяет корректность данных
    - Проверяет, что атрибут продукта с такими идентификаторами еще не существует
    - Создает и возвращает созданный атрибут продукта
    """
    return await product_attribute_service.create_product_attribute(request)


@router.put(
    "/{product_id}/{attribute_id}",
    response_model=ProductAttributeResponse,
    summary="Обновить атрибут продукта",
    description="Обновляет атрибут продукта по идентификаторам",
    responses={
        200: {"description": "Атрибут продукта успешно обновлен"},
        400: {"description": "Некорректные данные для атрибута продукта"},
        404: {"description": "Атрибут продукта не найден"},
    },
)
async def update_product_attribute(
    product_id: int,
    attribute_id: int,
    request: ProductAttributeUpdateRequest,
    product_attribute_service: ProductAttributeService = Depends(get_product_attribute_service),
):
    """
    Обновить атрибут продукта:
    - Проверяет корректность данных
    - Обновляет значение атрибута продукта
    - Возвращает обновленный атрибут продукта
    """
    return await product_attribute_service.update_product_attribute(product_id, attribute_id, request)


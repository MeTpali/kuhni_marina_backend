from fastapi import APIRouter, Depends, status

from api.deps import get_product_image_service
from services.product_images import ProductImageService
from core.schemas.product_images import (
    ProductImageCreateRequest,
    ProductImageResponse,
    ProductImageListResponse,
    ProductImageDeleteResponse,
)

router = APIRouter(
    prefix="/product-images",
    tags=["product-images"],
    responses={404: {"description": "Product image not found"}},
)


@router.get(
    "",
    response_model=ProductImageListResponse,
    summary="Получить все изображения продуктов",
    description="Возвращает список всех изображений продуктов",
)
async def get_product_images(
    product_image_service: ProductImageService = Depends(get_product_image_service),
):
    """
    Получить список всех изображений продуктов:
    - Возвращает все существующие изображения продуктов
    - Отсортированы по product_id и id
    """
    return await product_image_service.get_all_product_images()


@router.get(
    "/{product_image_id}",
    response_model=ProductImageResponse,
    summary="Получить изображение продукта по идентификатору",
    description="Возвращает изображение продукта с указанным идентификатором",
    responses={
        200: {"description": "Изображение продукта найдено"},
        404: {"description": "Изображение продукта не найдено"},
    },
)
async def get_product_image_by_id(
    product_image_id: int,
    product_image_service: ProductImageService = Depends(get_product_image_service),
):
    """
    Получить изображение продукта по идентификатору:
    - Возвращает изображение продукта, если оно существует
    - Возвращает ошибку 404, если изображение продукта не найдено
    """
    return await product_image_service.get_product_image_by_id(product_image_id)


@router.post(
    "",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать изображение продукта",
    description="Создает и возвращает новое изображение продукта",
    responses={
        201: {"description": "Изображение продукта успешно создано"},
        400: {"description": "Некорректные данные для изображения продукта"},
    },
)
async def create_product_image(
    request: ProductImageCreateRequest,
    product_image_service: ProductImageService = Depends(get_product_image_service),
):
    """
    Создать новое изображение продукта:
    - Проверяет корректность данных
    - Создает и возвращает созданное изображение продукта
    """
    return await product_image_service.create_product_image(request)


@router.delete(
    "/{product_image_id}",
    response_model=ProductImageDeleteResponse,
    summary="Удалить изображение продукта",
    description="Удаляет изображение продукта по идентификатору",
    responses={
        200: {"description": "Изображение продукта успешно удалено"},
        404: {"description": "Изображение продукта не найдено"},
    },
)
async def delete_product_image(
    product_image_id: int,
    product_image_service: ProductImageService = Depends(get_product_image_service),
):
    """
    Удалить изображение продукта:
    - Удаляет изображение продукта по идентификатору
    - Каскадное удаление связанных сущностей настроено в БД
    """
    return await product_image_service.delete_product_image(product_image_id)


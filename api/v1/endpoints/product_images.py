from fastapi import APIRouter, Depends, File, Form, HTTPException, status, UploadFile

from api.deps import get_product_image_service, get_product_repository
from repositories.products import ProductRepository
from services.product_images import ProductImageService
from core.schemas.product_images import (
    ProductImageCreateRequest,
    ProductImagesSetRequest,
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


@router.post(
    "/set",
    response_model=ProductImageListResponse,
    summary="Установить список изображений продукта",
    description="Заменяет все изображения продукта на переданный список ссылок. main_index — порядковый номер (1-based) главного; не задан или некорректен — главным первое.",
    responses={
        200: {"description": "Список изображений продукта обновлён"},
        400: {"description": "Некорректные данные"},
    },
)
async def set_product_images(
    request: ProductImagesSetRequest,
    product_image_service: ProductImageService = Depends(get_product_image_service),
):
    """
    Установить изображения продукта по id продукта:
    - product_id, image_urls (список строк), main_index (опционально, 1-based).
    - Если main_index не задан и у продукта нет главного — главным станет первое.
    - Если main_index некорректен — главным станет первое изображение из списка.
    """
    return await product_image_service.set_product_images(request)


@router.post(
    "/upload",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить изображение продукта",
    description="Загружает файл в Yandex Object Storage и создаёт запись изображения продукта. Структура в бакете: products/{product_id}/{uuid}.{ext}",
    responses={
        201: {"description": "Изображение загружено и создано"},
        400: {"description": "Некорректный файл или данные"},
        404: {"description": "Продукт не найден"},
    },
)
async def upload_product_image(
    product_id: int = Form(..., description="ID продукта"),
    is_main: bool = Form(False, description="Сделать изображение главным"),
    file: UploadFile = File(..., description="Файл изображения (JPEG, PNG, GIF, WebP; макс. 10 МБ)"),
    product_image_service: ProductImageService = Depends(get_product_image_service),
    product_repository: ProductRepository = Depends(get_product_repository),
):
    product = await product_repository.get_product_by_id(product_id, include_inactive=True)
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    return await product_image_service.upload_product_image(product_id, file, is_main)


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


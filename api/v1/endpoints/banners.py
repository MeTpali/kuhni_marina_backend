from fastapi import APIRouter, Depends, status

from api.deps import get_banner_service
from services.banners import BannerService
from core.schemas.banners import (
    BannerCreateRequest,
    BannerUpdateRequest,
    BannerResponse,
    BannerListResponse,
    BannerDeleteResponse,
)

router = APIRouter(
    prefix="/banners",
    tags=["banners"],
    responses={404: {"description": "Banner not found"}},
)


@router.get(
    "",
    response_model=BannerListResponse,
    summary="Получить все активные баннеры",
    description="Возвращает список всех активных баннеров",
)
async def get_banners(
    banner_service: BannerService = Depends(get_banner_service),
):
    """
    Получить список всех активных баннеров:
    - Возвращает только активные баннеры
    - Отсортированы по позиции и id
    """
    return await banner_service.get_all_banners()


@router.get(
    "/{banner_id}",
    response_model=BannerResponse,
    summary="Получить баннер по идентификатору",
    description="Возвращает баннер с указанным идентификатором",
    responses={
        200: {"description": "Баннер найден"},
        404: {"description": "Баннер не найден или неактивен"},
    },
)
async def get_banner_by_id(
    banner_id: int,
    banner_service: BannerService = Depends(get_banner_service),
):
    """
    Получить баннер по идентификатору:
    - Возвращает баннер, если он существует и активен
    - Возвращает ошибку 404, если баннер не найден или неактивен
    """
    return await banner_service.get_banner_by_id(banner_id)


@router.post(
    "",
    response_model=BannerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать баннер",
    description="Создает и возвращает новый баннер",
    responses={
        201: {"description": "Баннер успешно создан"},
        400: {"description": "Некорректные данные для баннера"},
    },
)
async def create_banner(
    request: BannerCreateRequest,
    banner_service: BannerService = Depends(get_banner_service),
):
    """
    Создать новый баннер:
    - Проверяет корректность данных
    - Создает и возвращает созданный баннер
    """
    return await banner_service.create_banner(request)


@router.put(
    "/{banner_id}",
    response_model=BannerResponse,
    summary="Обновить баннер",
    description="Обновляет баннер по идентификатору",
    responses={
        200: {"description": "Баннер успешно обновлен"},
        400: {"description": "Некорректные данные для баннера"},
        404: {"description": "Баннер не найден"},
    },
)
async def update_banner(
    banner_id: int,
    request: BannerUpdateRequest,
    banner_service: BannerService = Depends(get_banner_service),
):
    """
    Обновить баннер:
    - Проверяет корректность данных
    - Обновляет и возвращает обновленный баннер
    """
    return await banner_service.update_banner(banner_id, request)


@router.delete(
    "/{banner_id}",
    response_model=BannerDeleteResponse,
    summary="Удалить баннер",
    description="Удаляет баннер по идентификатору (деактивирует)",
    responses={
        200: {"description": "Баннер успешно удален"},
        404: {"description": "Баннер не найден"},
    },
)
async def delete_banner(
    banner_id: int,
    banner_service: BannerService = Depends(get_banner_service),
):
    """
    Удалить баннер:
    - Деактивирует баннер (устанавливает is_active=False)
    - Баннер не удаляется физически из базы данных
    """
    return await banner_service.delete_banner(banner_id)


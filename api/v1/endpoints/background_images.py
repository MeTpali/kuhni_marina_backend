from fastapi import APIRouter, Depends, status

from api.deps import get_background_image_service
from services.background_images import BackgroundImageService
from core.schemas.background_images import (
    BackgroundImageCreateRequest,
    BackgroundImageUpdateRequest,
    BackgroundImageResponse,
    BackgroundImageListResponse,
    BackgroundImageDeleteResponse,
)

router = APIRouter(
    prefix="/background-images",
    tags=["background-images"],
    responses={404: {"description": "Background image not found"}},
)


@router.get(
    "",
    response_model=BackgroundImageListResponse,
    summary="Получить все активные фоновые изображения",
    description="Возвращает список всех активных фоновых изображений",
)
async def get_background_images(
    background_image_service: BackgroundImageService = Depends(get_background_image_service),
):
    return await background_image_service.get_all_background_images()


@router.get(
    "/{background_image_id}",
    response_model=BackgroundImageResponse,
    summary="Получить фоновое изображение по идентификатору",
    description="Возвращает фоновое изображение с указанным идентификатором",
    responses={
        200: {"description": "Фоновое изображение найдено"},
        404: {"description": "Фоновое изображение не найдено или неактивно"},
    },
)
async def get_background_image_by_id(
    background_image_id: int,
    background_image_service: BackgroundImageService = Depends(get_background_image_service),
):
    return await background_image_service.get_background_image_by_id(background_image_id)


@router.post(
    "",
    response_model=BackgroundImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать фоновое изображение",
    description="Создает и возвращает новое фоновое изображение",
    responses={
        201: {"description": "Фоновое изображение успешно создано"},
        400: {"description": "Некорректные данные для фонового изображения"},
    },
)
async def create_background_image(
    request: BackgroundImageCreateRequest,
    background_image_service: BackgroundImageService = Depends(get_background_image_service),
):
    return await background_image_service.create_background_image(request)


@router.put(
    "/{background_image_id}",
    response_model=BackgroundImageResponse,
    summary="Обновить фоновое изображение",
    description="Обновляет фоновое изображение по идентификатору",
    responses={
        200: {"description": "Фоновое изображение успешно обновлено"},
        400: {"description": "Некорректные данные для фонового изображения"},
        404: {"description": "Фоновое изображение не найдено"},
    },
)
async def update_background_image(
    background_image_id: int,
    request: BackgroundImageUpdateRequest,
    background_image_service: BackgroundImageService = Depends(get_background_image_service),
):
    return await background_image_service.update_background_image(background_image_id, request)


@router.delete(
    "/{background_image_id}",
    response_model=BackgroundImageDeleteResponse,
    summary="Удалить фоновое изображение",
    description="Удаляет фоновое изображение по идентификатору (деактивирует)",
    responses={
        200: {"description": "Фоновое изображение успешно удалено"},
        404: {"description": "Фоновое изображение не найдено"},
    },
)
async def delete_background_image(
    background_image_id: int,
    background_image_service: BackgroundImageService = Depends(get_background_image_service),
):
    return await background_image_service.delete_background_image(background_image_id)

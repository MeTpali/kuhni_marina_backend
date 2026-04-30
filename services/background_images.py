import logging

from fastapi import HTTPException, status

from repositories.background_images import BackgroundImageRepository
from core.schemas.background_images import (
    BackgroundImageCreateRequest,
    BackgroundImageUpdateRequest,
    BackgroundImageResponse,
    BackgroundImageListResponse,
    BackgroundImageDeleteResponse,
)

logger = logging.getLogger(__name__)


class BackgroundImageService:
    def __init__(self, repository: BackgroundImageRepository):
        self.repository = repository

    async def get_all_background_images(self) -> BackgroundImageListResponse:
        logger.info("Fetching all active background images via service")
        background_images = await self.repository.get_all_active_background_images()
        items = [
            BackgroundImageResponse(
                id=background_image.id,
                url=background_image.url,
                is_active=background_image.is_active,
                message=None,
            )
            for background_image in background_images
        ]

        response = BackgroundImageListResponse(
            items=items,
            message="Список фоновых изображений успешно получен",
        )
        logger.info("Successfully fetched %d active background images", len(items))
        return response

    async def get_background_image_by_id(self, background_image_id: int) -> BackgroundImageResponse:
        logger.info("Fetching background image by id: %s via service", background_image_id)
        background_image = await self.repository.get_background_image_by_id(background_image_id)
        if not background_image:
            logger.error("Background image with id %s not found", background_image_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Фоновое изображение с id {background_image_id} не найдено",
            )

        if not background_image.is_active:
            logger.error("Background image with id %s is not active", background_image_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Это фоновое изображение недоступно. Оно было удалено или деактивировано.",
            )

        response = BackgroundImageResponse(
            id=background_image.id,
            url=background_image.url,
            is_active=background_image.is_active,
            message="Фоновое изображение успешно найдено",
        )
        logger.info("Background image with id %s successfully retrieved", background_image_id)
        return response

    async def create_background_image(
        self,
        request: BackgroundImageCreateRequest,
    ) -> BackgroundImageResponse:
        logger.info("Creating background image via service")

        if not request.url or len(request.url.strip()) == 0:
            logger.error("Background image url is empty")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL фонового изображения обязателен для заполнения",
            )

        background_image = await self.repository.create_background_image(request)

        response = BackgroundImageResponse(
            id=background_image.id,
            url=background_image.url,
            is_active=background_image.is_active,
            message="Фоновое изображение успешно создано",
        )
        logger.info("Background image created with id %s via service", background_image.id)
        return response

    async def update_background_image(
        self,
        background_image_id: int,
        request: BackgroundImageUpdateRequest,
    ) -> BackgroundImageResponse:
        logger.info("Updating background image via service with id %s", background_image_id)

        if not request.url or len(request.url.strip()) == 0:
            logger.error("Background image url is empty")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL фонового изображения обязателен для заполнения",
            )

        background_image = await self.repository.update_background_image(background_image_id, request)
        if not background_image:
            logger.error("Background image with id %s not found for update", background_image_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Фоновое изображение с id {background_image_id} не найдено",
            )

        response = BackgroundImageResponse(
            id=background_image.id,
            url=background_image.url,
            is_active=background_image.is_active,
            message="Фоновое изображение успешно обновлено",
        )
        logger.info(
            "Background image with id %s successfully updated via service",
            background_image_id,
        )
        return response

    async def delete_background_image(self, background_image_id: int) -> BackgroundImageDeleteResponse:
        logger.info("Deleting background image via service with id %s", background_image_id)
        success = await self.repository.deactivate_background_image(background_image_id)
        if not success:
            logger.error("Background image with id %s not found for deletion", background_image_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Фоновое изображение с id {background_image_id} не найдено",
            )

        response = BackgroundImageDeleteResponse(
            background_image_id=background_image_id,
            message="Фоновое изображение успешно удалено",
        )
        logger.info("Background image with id %s successfully deleted via service", background_image_id)
        return response

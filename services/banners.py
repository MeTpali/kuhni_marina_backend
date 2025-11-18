import logging

from fastapi import HTTPException, status

from repositories.banners import BannerRepository
from core.schemas.banners import (
    BannerCreateRequest,
    BannerResponse,
    BannerListResponse,
    BannerDeleteResponse,
)

logger = logging.getLogger(__name__)


class BannerService:
    def __init__(self, repository: BannerRepository):
        self.repository = repository

    async def get_all_banners(self) -> BannerListResponse:
        """
        Получить список всех активных баннеров.
        """
        logger.info("Fetching all active banners via service")
        banners = await self.repository.get_all_active_banners()
        items = [
            BannerResponse(
                id=banner.id,
                title=banner.title,
                image_url=banner.image_url,
                link_url=banner.link_url,
                position=banner.position,
                is_active=banner.is_active,
                message=None,
            )
            for banner in banners
        ]

        response = BannerListResponse(
            items=items,
            message="Список баннеров успешно получен",
        )
        logger.info("Successfully fetched %d active banners", len(items))
        return response

    async def get_banner_by_id(self, banner_id: int) -> BannerResponse:
        """
        Получить баннер по идентификатору.
        """
        logger.info("Fetching banner by id: %s via service", banner_id)
        banner = await self.repository.get_banner_by_id(banner_id)
        if not banner:
            logger.error("Banner with id %s not found", banner_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Баннер с id {banner_id} не найден",
            )

        if not banner.is_active:
            logger.error("Banner with id %s is not active", banner_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Этот баннер недоступен. Он был удален или деактивирован.",
            )

        response = BannerResponse(
            id=banner.id,
            title=banner.title,
            image_url=banner.image_url,
            link_url=banner.link_url,
            position=banner.position,
            is_active=banner.is_active,
            message="Баннер успешно найден",
        )
        logger.info("Banner with id %s successfully retrieved", banner_id)
        return response

    async def create_banner(
        self,
        request: BannerCreateRequest,
    ) -> BannerResponse:
        """
        Создать новый баннер.
        """
        logger.info("Creating banner via service with title '%s'", request.title)

        if len(request.title.strip()) < 2:
            logger.error("Banner title too short: '%s'", request.title)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Заголовок баннера должен содержать минимум 2 символа",
            )

        if not request.image_url or len(request.image_url.strip()) == 0:
            logger.error("Banner image_url is empty")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL изображения обязателен для заполнения",
            )

        banner = await self.repository.create_banner(request)

        response = BannerResponse(
            id=banner.id,
            title=banner.title,
            image_url=banner.image_url,
            link_url=banner.link_url,
            position=banner.position,
            is_active=banner.is_active,
            message="Баннер успешно создан",
        )
        logger.info("Banner created with id %s via service", banner.id)
        return response

    async def delete_banner(self, banner_id: int) -> BannerDeleteResponse:
        """
        Удалить баннер по идентификатору (soft delete через is_active=False).
        """
        logger.info("Deleting banner via service with id %s", banner_id)
        success = await self.repository.deactivate_banner(banner_id)
        if not success:
            logger.error("Banner with id %s not found for deletion", banner_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Баннер с id {banner_id} не найден",
            )

        response = BannerDeleteResponse(
            banner_id=banner_id,
            message="Баннер успешно удален",
        )
        logger.info("Banner with id %s successfully deleted via service", banner_id)
        return response


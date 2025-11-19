from typing import List, Optional
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.banners import Banner
from core.schemas.banners import BannerCreateRequest, BannerUpdateRequest

logger = logging.getLogger(__name__)


class BannerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active_banners(self) -> List[Banner]:
        """
        Получить список всех активных баннеров.
        """
        logger.info("Fetching all active banners")
        query = select(Banner).where(Banner.is_active == True).order_by(Banner.position, Banner.id)
        result = await self.session.execute(query)
        banners = result.scalars().all()
        logger.info("Retrieved %d active banners", len(banners))
        return banners

    async def get_banner_by_id(self, banner_id: int) -> Optional[Banner]:
        """
        Получить баннер по идентификатору.
        """
        logger.info("Fetching banner with id %s", banner_id)
        query = select(Banner).where(Banner.id == banner_id)
        result = await self.session.execute(query)
        banner = result.scalar_one_or_none()

        if banner is None:
            logger.warning("Banner with id %s not found", banner_id)
        return banner

    async def create_banner(self, request: BannerCreateRequest) -> Banner:
        """
        Создать новый баннер.
        """
        logger.info("Creating banner with title '%s'", request.title)
        banner = Banner(
            title=request.title,
            image_url=request.image_url,
            link_url=request.link_url,
            position=request.position,
            is_active=request.is_active if request.is_active is not None else True,
        )

        self.session.add(banner)
        await self.session.commit()
        await self.session.refresh(banner)

        logger.info("Banner created with id %s", banner.id)
        return banner

    async def update_banner(
        self, banner_id: int, request: BannerUpdateRequest
    ) -> Optional[Banner]:
        """
        Обновить баннер по идентификатору.
        """
        logger.info("Updating banner with id %s", banner_id)
        banner = await self.get_banner_by_id(banner_id)
        if banner is None:
            logger.warning("Banner with id %s not found for update", banner_id)
            return None

        banner.title = request.title
        banner.image_url = request.image_url
        banner.link_url = request.link_url
        banner.position = request.position
        banner.is_active = request.is_active if request.is_active is not None else banner.is_active

        await self.session.commit()
        await self.session.refresh(banner)

        logger.info("Banner with id %s successfully updated", banner_id)
        return banner

    async def deactivate_banner(self, banner_id: int) -> bool:
        """
        Деактивировать баннер по идентификатору (soft delete).
        """
        logger.info("Deactivating banner with id %s", banner_id)
        banner = await self.get_banner_by_id(banner_id)
        if banner is None:
            logger.warning("Banner with id %s not found for deactivation", banner_id)
            return False

        banner.is_active = False
        await self.session.commit()

        logger.info("Banner with id %s successfully deactivated", banner_id)
        return True


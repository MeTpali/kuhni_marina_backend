from typing import List, Optional
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.background_images import BackgroundImage
from core.schemas.background_images import (
    BackgroundImageCreateRequest,
    BackgroundImageUpdateRequest,
)

logger = logging.getLogger(__name__)


class BackgroundImageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active_background_images(self) -> List[BackgroundImage]:
        logger.info("Fetching all active background images")
        query = (
            select(BackgroundImage)
            .where(BackgroundImage.is_active == True)
            .order_by(BackgroundImage.id)
        )
        result = await self.session.execute(query)
        background_images = result.scalars().all()
        logger.info("Retrieved %d active background images", len(background_images))
        return background_images

    async def get_background_image_by_id(self, background_image_id: int) -> Optional[BackgroundImage]:
        logger.info("Fetching background image with id %s", background_image_id)
        query = select(BackgroundImage).where(BackgroundImage.id == background_image_id)
        result = await self.session.execute(query)
        background_image = result.scalar_one_or_none()

        if background_image is None:
            logger.warning("Background image with id %s not found", background_image_id)
        return background_image

    async def create_background_image(self, request: BackgroundImageCreateRequest) -> BackgroundImage:
        logger.info("Creating background image")
        background_image = BackgroundImage(
            url=request.url,
            is_active=request.is_active if request.is_active is not None else True,
        )

        self.session.add(background_image)
        await self.session.commit()
        await self.session.refresh(background_image)

        logger.info("Background image created with id %s", background_image.id)
        return background_image

    async def update_background_image(
        self,
        background_image_id: int,
        request: BackgroundImageUpdateRequest,
    ) -> Optional[BackgroundImage]:
        logger.info("Updating background image with id %s", background_image_id)
        background_image = await self.get_background_image_by_id(background_image_id)
        if background_image is None:
            logger.warning("Background image with id %s not found for update", background_image_id)
            return None

        background_image.url = request.url
        background_image.is_active = (
            request.is_active if request.is_active is not None else background_image.is_active
        )

        await self.session.commit()
        await self.session.refresh(background_image)

        logger.info("Background image with id %s successfully updated", background_image_id)
        return background_image

    async def deactivate_background_image(self, background_image_id: int) -> bool:
        logger.info("Deactivating background image with id %s", background_image_id)
        background_image = await self.get_background_image_by_id(background_image_id)
        if background_image is None:
            logger.warning("Background image with id %s not found for deactivation", background_image_id)
            return False

        background_image.is_active = False
        await self.session.commit()

        logger.info("Background image with id %s successfully deactivated", background_image_id)
        return True

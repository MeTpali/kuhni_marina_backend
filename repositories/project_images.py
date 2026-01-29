from typing import List, Optional
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.project_images import ProjectImage
from core.schemas.project_images import ProjectImageCreateRequest

logger = logging.getLogger(__name__)


class ProjectImageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_project_images(self) -> List[ProjectImage]:
        """
        Получить список всех изображений проектов.
        """
        logger.info("Fetching all project images")
        query = select(ProjectImage).order_by(ProjectImage.project_id, ProjectImage.id)
        result = await self.session.execute(query)
        project_images = result.scalars().all()
        logger.info("Retrieved %d project images", len(project_images))
        return project_images

    async def get_project_image_by_id(self, project_image_id: int) -> Optional[ProjectImage]:
        """
        Получить изображение проекта по идентификатору.
        """
        logger.info("Fetching project image with id %s", project_image_id)
        query = select(ProjectImage).where(ProjectImage.id == project_image_id)
        result = await self.session.execute(query)
        project_image = result.scalar_one_or_none()

        if project_image is None:
            logger.warning("Project image with id %s not found", project_image_id)
        return project_image

    async def get_project_images_by_project_id(self, project_id: int) -> List[ProjectImage]:
        """
        Получить список изображений проекта по идентификатору проекта.
        """
        logger.info("Fetching project images for project_id %s", project_id)
        query = select(ProjectImage).where(ProjectImage.project_id == project_id).order_by(ProjectImage.id)
        result = await self.session.execute(query)
        project_images = result.scalars().all()
        logger.info("Retrieved %d project images for project_id %s", len(project_images), project_id)
        return project_images

    async def create_project_image(self, request: ProjectImageCreateRequest) -> ProjectImage:
        """
        Создать новое изображение проекта.
        """
        logger.info("Creating project image for project_id %s", request.project_id)
        project_image = ProjectImage(
            project_id=request.project_id,
            image_url=request.image_url,
            is_main=request.is_main if request.is_main is not None else False,
        )

        self.session.add(project_image)
        await self.session.commit()
        await self.session.refresh(project_image)

        logger.info("Project image created with id %s", project_image.id)
        return project_image

    async def create_multiple_project_images(
        self, requests: List[ProjectImageCreateRequest]
    ) -> List[ProjectImage]:
        """
        Создать несколько изображений проекта.
        """
        logger.info("Creating %d project images", len(requests))
        project_images = []
        for request in requests:
            project_image = ProjectImage(
                project_id=request.project_id,
                image_url=request.image_url,
                is_main=request.is_main if request.is_main is not None else False,
            )
            project_images.append(project_image)
            self.session.add(project_image)

        await self.session.commit()
        for project_image in project_images:
            await self.session.refresh(project_image)

        logger.info("Successfully created %d project images", len(project_images))
        return project_images

    async def delete_project_image(self, project_image_id: int) -> bool:
        """
        Удалить изображение проекта по идентификатору.
        """
        logger.info("Deleting project image with id %s", project_image_id)
        project_image = await self.get_project_image_by_id(project_image_id)
        if project_image is None:
            logger.warning("Project image with id %s not found for deletion", project_image_id)
            return False

        await self.session.delete(project_image)
        await self.session.commit()

        logger.info("Project image with id %s successfully deleted", project_image_id)
        return True


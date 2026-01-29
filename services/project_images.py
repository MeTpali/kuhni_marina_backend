import logging

from fastapi import HTTPException, status

from repositories.project_images import ProjectImageRepository
from core.schemas.project_images import (
    ProjectImageCreateRequest,
    ProjectImageCreateBulkRequest,
    ProjectImageResponse,
    ProjectImageListResponse,
    ProjectImageDeleteResponse,
)

logger = logging.getLogger(__name__)


class ProjectImageService:
    def __init__(self, repository: ProjectImageRepository):
        self.repository = repository

    async def get_all_project_images(self) -> ProjectImageListResponse:
        """
        Получить список всех изображений проектов.
        """
        logger.info("Fetching all project images via service")
        project_images = await self.repository.get_all_project_images()
        items = [
            ProjectImageResponse(
                id=pi.id,
                project_id=pi.project_id,
                image_url=pi.image_url,
                is_main=pi.is_main,
                message=None,
            )
            for pi in project_images
        ]

        response = ProjectImageListResponse(
            items=items,
            message="Список изображений проектов успешно получен",
        )
        logger.info("Successfully fetched %d project images", len(items))
        return response

    async def get_project_image_by_id(self, project_image_id: int) -> ProjectImageResponse:
        """
        Получить изображение проекта по идентификатору.
        """
        logger.info("Fetching project image by id: %s via service", project_image_id)
        project_image = await self.repository.get_project_image_by_id(project_image_id)
        if not project_image:
            logger.error("Project image with id %s not found", project_image_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Изображение проекта с id {project_image_id} не найдено",
            )

        response = ProjectImageResponse(
            id=project_image.id,
            project_id=project_image.project_id,
            image_url=project_image.image_url,
            is_main=project_image.is_main,
            message="Изображение проекта успешно найдено",
        )
        logger.info("Project image with id %s successfully retrieved", project_image_id)
        return response

    async def create_project_image(
        self,
        request: ProjectImageCreateRequest,
    ) -> ProjectImageResponse:
        """
        Создать новое изображение проекта.
        """
        logger.info("Creating project image via service for project_id %s", request.project_id)

        if not request.image_url or len(request.image_url.strip()) == 0:
            logger.error("Project image image_url is empty")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL изображения обязателен для заполнения",
            )

        project_image = await self.repository.create_project_image(request)

        response = ProjectImageResponse(
            id=project_image.id,
            project_id=project_image.project_id,
            image_url=project_image.image_url,
            is_main=project_image.is_main,
            message="Изображение проекта успешно создано",
        )
        logger.info("Project image created with id %s via service", project_image.id)
        return response

    async def create_multiple_project_images(
        self,
        request: ProjectImageCreateBulkRequest,
    ) -> ProjectImageListResponse:
        """
        Создать несколько изображений проекта.
        """
        logger.info("Creating %d project images via service", len(request.images))

        if not request.images or len(request.images) == 0:
            logger.error("No images provided in bulk request")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Список изображений не может быть пустым",
            )

        # Валидация всех изображений
        for img_request in request.images:
            if not img_request.image_url or len(img_request.image_url.strip()) == 0:
                logger.error("Project image image_url is empty in bulk request")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="URL изображения обязателен для заполнения",
                )

        project_images = await self.repository.create_multiple_project_images(request.images)

        items = [
            ProjectImageResponse(
                id=pi.id,
                project_id=pi.project_id,
                image_url=pi.image_url,
                is_main=pi.is_main,
                message=None,
            )
            for pi in project_images
        ]

        response = ProjectImageListResponse(
            items=items,
            message=f"Успешно создано {len(items)} изображений проекта",
        )
        logger.info("Successfully created %d project images via service", len(items))
        return response

    async def delete_project_image(self, project_image_id: int) -> ProjectImageDeleteResponse:
        """
        Удалить изображение проекта по идентификатору.
        """
        logger.info("Deleting project image via service with id %s", project_image_id)
        success = await self.repository.delete_project_image(project_image_id)
        if not success:
            logger.error("Project image with id %s not found for deletion", project_image_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Изображение проекта с id {project_image_id} не найдено",
            )

        response = ProjectImageDeleteResponse(
            project_image_id=project_image_id,
            message="Изображение проекта успешно удалено",
        )
        logger.info("Project image with id %s successfully deleted via service", project_image_id)
        return response


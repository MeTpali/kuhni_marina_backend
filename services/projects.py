import logging

from fastapi import HTTPException, status

from repositories.projects import ProjectRepository
from repositories.project_images import ProjectImageRepository
from repositories.project_products import ProjectProductRepository
from core.schemas.projects import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectDeleteResponse,
)
from core.schemas.project_images import ProjectImageResponse

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(
        self,
        repository: ProjectRepository,
        project_image_repository: ProjectImageRepository,
        project_product_repository: ProjectProductRepository,
    ):
        self.repository = repository
        self.project_image_repository = project_image_repository
        self.project_product_repository = project_product_repository

    async def get_all_projects(self) -> ProjectListResponse:
        """
        Получить список всех проектов.
        """
        logger.info("Fetching all projects via service")
        projects = await self.repository.get_all_projects()
        items = [
            ProjectResponse(
                id=project.id,
                name=project.name,
                description=project.description,
                location=project.location,
                created_at=project.created_at,
                message=None,
            )
            for project in projects
        ]

        response = ProjectListResponse(
            items=items,
            message="Список проектов успешно получен",
        )
        logger.info("Successfully fetched %d projects", len(items))
        return response

    async def get_project_by_id(self, project_id: int) -> ProjectDetailResponse:
        """
        Получить проект по идентификатору с изображениями и продуктами.
        """
        logger.info("Fetching project by id: %s via service", project_id)
        project = await self.repository.get_project_by_id(project_id)
        if not project:
            logger.error("Project with id %s not found", project_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Проект с id {project_id} не найден",
            )

        # Получаем изображения проекта
        project_images = await self.project_image_repository.get_project_images_by_project_id(project_id)
        images = [
            ProjectImageResponse(
                id=pi.id,
                project_id=pi.project_id,
                image_url=pi.image_url,
                is_main=pi.is_main,
                message=None,
            )
            for pi in project_images
        ]

        # Получаем ID продуктов проекта
        product_ids = await self.project_product_repository.get_product_ids_by_project_id(project_id)

        response = ProjectDetailResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            location=project.location,
            created_at=project.created_at,
            images=images,
            product_ids=product_ids,
            message="Проект успешно найден",
        )
        logger.info("Project with id %s successfully retrieved", project_id)
        return response

    async def get_projects_by_product_id(self, product_id: int) -> ProjectListResponse:
        """
        Получить список проектов по идентификатору продукта.
        """
        logger.info("Fetching projects by product_id: %s via service", product_id)
        project_ids = await self.project_product_repository.get_project_ids_by_product_id(product_id)
        
        projects = []
        for project_id in project_ids:
            project = await self.repository.get_project_by_id(project_id)
            if project:
                projects.append(project)

        items = [
            ProjectResponse(
                id=project.id,
                name=project.name,
                description=project.description,
                location=project.location,
                created_at=project.created_at,
                message=None,
            )
            for project in projects
        ]

        response = ProjectListResponse(
            items=items,
            message=f"Список проектов для продукта с id {product_id} успешно получен",
        )
        logger.info("Successfully fetched %d projects for product_id %s", len(items), product_id)
        return response

    async def create_project(
        self,
        request: ProjectCreateRequest,
    ) -> ProjectResponse:
        """
        Создать новый проект.
        """
        logger.info("Creating project via service with name '%s'", request.name)

        if len(request.name.strip()) < 2:
            logger.error("Project name too short: '%s'", request.name)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Название проекта должно содержать минимум 2 символа",
            )

        project = await self.repository.create_project(request)

        response = ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            location=project.location,
            created_at=project.created_at,
            message="Проект успешно создан",
        )
        logger.info("Project created with id %s via service", project.id)
        return response

    async def update_project(
        self,
        project_id: int,
        request: ProjectUpdateRequest,
    ) -> ProjectResponse:
        """
        Обновить проект по идентификатору.
        """
        logger.info("Updating project via service with id %s", project_id)

        if request.name is not None and len(request.name.strip()) < 2:
            logger.error("Project name too short: '%s'", request.name)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Название проекта должно содержать минимум 2 символа",
            )

        project = await self.repository.update_project(project_id, request)
        if not project:
            logger.error("Project with id %s not found for update", project_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Проект с id {project_id} не найден",
            )

        response = ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            location=project.location,
            created_at=project.created_at,
            message="Проект успешно обновлен",
        )
        logger.info("Project with id %s successfully updated via service", project_id)
        return response

    async def delete_project(self, project_id: int) -> ProjectDeleteResponse:
        """
        Удалить проект по идентификатору.
        """
        logger.info("Deleting project via service with id %s", project_id)
        success = await self.repository.delete_project(project_id)
        if not success:
            logger.error("Project with id %s not found for deletion", project_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Проект с id {project_id} не найден",
            )

        response = ProjectDeleteResponse(
            project_id=project_id,
            message="Проект успешно удален",
        )
        logger.info("Project with id %s successfully deleted via service", project_id)
        return response


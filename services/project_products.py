import logging

from fastapi import HTTPException, status

from repositories.project_products import ProjectProductRepository
from core.schemas.project_products import (
    ProjectProductCreateRequest,
    ProjectProductResponse,
    ProjectProductListResponse,
    ProjectProductDeleteResponse,
    ProjectIdsByProductResponse,
)

logger = logging.getLogger(__name__)


class ProjectProductService:
    def __init__(self, repository: ProjectProductRepository):
        self.repository = repository

    async def get_all_project_products(self) -> ProjectProductListResponse:
        """
        Получить список всех связей проектов с продуктами.
        """
        logger.info("Fetching all project products via service")
        project_products = await self.repository.get_all_project_products()
        items = [
            ProjectProductResponse(
                project_id=pp.project_id,
                product_id=pp.product_id,
                message=None,
            )
            for pp in project_products
        ]

        response = ProjectProductListResponse(
            items=items,
            message="Список связей проектов с продуктами успешно получен",
        )
        logger.info("Successfully fetched %d project products", len(items))
        return response

    async def create_project_product(
        self,
        request: ProjectProductCreateRequest,
    ) -> ProjectProductResponse:
        """
        Создать новую связь проекта с продуктом.
        """
        logger.info("Creating project product via service for project_id %s and product_id %s", request.project_id, request.product_id)

        # Проверяем, не существует ли уже такая связь
        existing = await self.repository.get_project_product_by_id(request.project_id, request.product_id)
        if existing:
            logger.error("Project product with project_id %s and product_id %s already exists", request.project_id, request.product_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Связь проекта с project_id {request.project_id} и product_id {request.product_id} уже существует",
            )

        project_product = await self.repository.create_project_product(request)

        response = ProjectProductResponse(
            project_id=project_product.project_id,
            product_id=project_product.product_id,
            message="Связь проекта с продуктом успешно создана",
        )
        logger.info("Project product created for project_id %s and product_id %s via service", project_product.project_id, project_product.product_id)
        return response

    async def get_project_ids_by_product_id(self, product_id: int) -> ProjectIdsByProductResponse:
        """
        Получить список идентификаторов проектов по идентификатору продукта.
        """
        logger.info("Fetching project ids by product_id: %s via service", product_id)
        project_ids = await self.repository.get_project_ids_by_product_id(product_id)

        response = ProjectIdsByProductResponse(
            product_id=product_id,
            project_ids=project_ids,
            message=f"Список идентификаторов проектов для продукта с id {product_id} успешно получен",
        )
        logger.info("Successfully fetched %d project ids for product_id %s", len(project_ids), product_id)
        return response

    async def delete_project_product(
        self,
        project_id: int,
        product_id: int,
    ) -> ProjectProductDeleteResponse:
        """
        Удалить связь проекта с продуктом по идентификаторам.
        """
        logger.info("Deleting project product via service with project_id %s and product_id %s", project_id, product_id)
        success = await self.repository.delete_project_product(project_id, product_id)
        if not success:
            logger.error("Project product with project_id %s and product_id %s not found for deletion", project_id, product_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Связь проекта с project_id {project_id} и product_id {product_id} не найдена",
            )

        response = ProjectProductDeleteResponse(
            project_id=project_id,
            product_id=product_id,
            message="Связь проекта с продуктом успешно удалена",
        )
        logger.info("Project product with project_id %s and product_id %s successfully deleted via service", project_id, product_id)
        return response


from typing import List, Optional
import logging

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.project_products import ProjectProduct
from core.schemas.project_products import ProjectProductCreateRequest

logger = logging.getLogger(__name__)


class ProjectProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_project_products(self) -> List[ProjectProduct]:
        """
        Получить список всех связей проектов с продуктами.
        """
        logger.info("Fetching all project products")
        query = select(ProjectProduct).order_by(ProjectProduct.project_id, ProjectProduct.product_id)
        result = await self.session.execute(query)
        project_products = result.scalars().all()
        logger.info("Retrieved %d project products", len(project_products))
        return project_products

    async def get_project_product_by_id(
        self, project_id: int, product_id: int
    ) -> Optional[ProjectProduct]:
        """
        Получить связь проекта с продуктом по идентификаторам.
        """
        logger.info("Fetching project product with project_id %s and product_id %s", project_id, product_id)
        query = select(ProjectProduct).where(
            and_(
                ProjectProduct.project_id == project_id,
                ProjectProduct.product_id == product_id
            )
        )
        result = await self.session.execute(query)
        project_product = result.scalar_one_or_none()

        if project_product is None:
            logger.warning("Project product with project_id %s and product_id %s not found", project_id, product_id)
        return project_product

    async def create_project_product(
        self, request: ProjectProductCreateRequest
    ) -> ProjectProduct:
        """
        Создать новую связь проекта с продуктом.
        """
        logger.info("Creating project product for project_id %s and product_id %s", request.project_id, request.product_id)
        project_product = ProjectProduct(
            project_id=request.project_id,
            product_id=request.product_id,
        )

        self.session.add(project_product)
        await self.session.commit()
        await self.session.refresh(project_product)

        logger.info("Project product created for project_id %s and product_id %s", request.project_id, request.product_id)
        return project_product

    async def get_project_ids_by_product_id(self, product_id: int) -> List[int]:
        """
        Получить список идентификаторов проектов по идентификатору продукта.
        """
        logger.info("Fetching project ids for product_id %s", product_id)
        query = select(ProjectProduct.project_id).where(ProjectProduct.product_id == product_id)
        result = await self.session.execute(query)
        project_ids = result.scalars().all()
        logger.info("Retrieved %d project ids for product_id %s", len(project_ids), product_id)
        return list(project_ids)

    async def get_product_ids_by_project_id(self, project_id: int) -> List[int]:
        """
        Получить список идентификаторов продуктов по идентификатору проекта.
        """
        logger.info("Fetching product ids for project_id %s", project_id)
        query = select(ProjectProduct.product_id).where(ProjectProduct.project_id == project_id)
        result = await self.session.execute(query)
        product_ids = result.scalars().all()
        logger.info("Retrieved %d product ids for project_id %s", len(product_ids), project_id)
        return list(product_ids)

    async def delete_project_product(
        self, project_id: int, product_id: int
    ) -> bool:
        """
        Удалить связь проекта с продуктом по идентификаторам.
        """
        logger.info("Deleting project product with project_id %s and product_id %s", project_id, product_id)
        project_product = await self.get_project_product_by_id(project_id, product_id)
        if project_product is None:
            logger.warning("Project product with project_id %s and product_id %s not found for deletion", project_id, product_id)
            return False

        await self.session.delete(project_product)
        await self.session.commit()

        logger.info("Project product with project_id %s and product_id %s successfully deleted", project_id, product_id)
        return True


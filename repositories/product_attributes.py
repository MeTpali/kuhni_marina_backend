from typing import List, Optional
import logging

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.product_attributes import ProductAttribute
from core.schemas.product_attributes import (
    ProductAttributeCreateRequest,
    ProductAttributeUpdateRequest,
)

logger = logging.getLogger(__name__)


class ProductAttributeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_product_attributes(self) -> List[ProductAttribute]:
        """
        Получить список всех атрибутов продуктов.
        """
        logger.info("Fetching all product attributes")
        query = select(ProductAttribute).order_by(ProductAttribute.product_id, ProductAttribute.attribute_id)
        result = await self.session.execute(query)
        product_attributes = result.scalars().all()
        logger.info("Retrieved %d product attributes", len(product_attributes))
        return product_attributes

    async def get_product_attribute_by_id(
        self, product_id: int, attribute_id: int
    ) -> Optional[ProductAttribute]:
        """
        Получить атрибут продукта по идентификаторам продукта и атрибута.
        """
        logger.info("Fetching product attribute with product_id %s and attribute_id %s", product_id, attribute_id)
        query = select(ProductAttribute).where(
            and_(
                ProductAttribute.product_id == product_id,
                ProductAttribute.attribute_id == attribute_id
            )
        )
        result = await self.session.execute(query)
        product_attribute = result.scalar_one_or_none()

        if product_attribute is None:
            logger.warning("Product attribute with product_id %s and attribute_id %s not found", product_id, attribute_id)
        return product_attribute

    async def create_product_attribute(
        self, request: ProductAttributeCreateRequest
    ) -> ProductAttribute:
        """
        Создать новый атрибут продукта.
        """
        logger.info("Creating product attribute for product_id %s and attribute_id %s", request.product_id, request.attribute_id)
        product_attribute = ProductAttribute(
            product_id=request.product_id,
            attribute_id=request.attribute_id,
            value=request.value,
        )

        self.session.add(product_attribute)
        await self.session.commit()
        await self.session.refresh(product_attribute)

        logger.info("Product attribute created for product_id %s and attribute_id %s", request.product_id, request.attribute_id)
        return product_attribute

    async def update_product_attribute(
        self, product_id: int, attribute_id: int, request: ProductAttributeUpdateRequest
    ) -> Optional[ProductAttribute]:
        """
        Обновить атрибут продукта по идентификаторам.
        """
        logger.info("Updating product attribute with product_id %s and attribute_id %s", product_id, attribute_id)
        product_attribute = await self.get_product_attribute_by_id(product_id, attribute_id)
        if product_attribute is None:
            logger.warning("Product attribute with product_id %s and attribute_id %s not found for update", product_id, attribute_id)
            return None

        product_attribute.value = request.value

        await self.session.commit()
        await self.session.refresh(product_attribute)

        logger.info("Product attribute with product_id %s and attribute_id %s successfully updated", product_id, attribute_id)
        return product_attribute


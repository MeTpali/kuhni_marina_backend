from typing import List, Optional
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.product_images import ProductImage
from core.schemas.product_images import ProductImageCreateRequest

logger = logging.getLogger(__name__)


class ProductImageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_product_images(self) -> List[ProductImage]:
        """
        Получить список всех изображений продуктов.
        """
        logger.info("Fetching all product images")
        query = select(ProductImage).order_by(ProductImage.product_id, ProductImage.id)
        result = await self.session.execute(query)
        product_images = result.scalars().all()
        logger.info("Retrieved %d product images", len(product_images))
        return product_images

    async def get_product_image_by_id(self, product_image_id: int) -> Optional[ProductImage]:
        """
        Получить изображение продукта по идентификатору.
        """
        logger.info("Fetching product image with id %s", product_image_id)
        query = select(ProductImage).where(ProductImage.id == product_image_id)
        result = await self.session.execute(query)
        product_image = result.scalar_one_or_none()

        if product_image is None:
            logger.warning("Product image with id %s not found", product_image_id)
        return product_image

    async def create_product_image(self, request: ProductImageCreateRequest) -> ProductImage:
        """
        Создать новое изображение продукта.
        """
        logger.info("Creating product image for product_id %s", request.product_id)
        product_image = ProductImage(
            product_id=request.product_id,
            image_url=request.image_url,
            is_main=request.is_main if request.is_main is not None else False,
        )

        self.session.add(product_image)
        await self.session.commit()
        await self.session.refresh(product_image)

        logger.info("Product image created with id %s", product_image.id)
        return product_image

    async def delete_product_image(self, product_image_id: int) -> bool:
        """
        Удалить изображение продукта по идентификатору.
        """
        logger.info("Deleting product image with id %s", product_image_id)
        product_image = await self.get_product_image_by_id(product_image_id)
        if product_image is None:
            logger.warning("Product image with id %s not found for deletion", product_image_id)
            return False

        await self.session.delete(product_image)
        await self.session.commit()

        logger.info("Product image with id %s successfully deleted", product_image_id)
        return True


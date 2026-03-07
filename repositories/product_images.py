from typing import List, Optional
import logging

from sqlalchemy import delete, select, update
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

    async def get_product_images_by_product_id(self, product_id: int) -> List[ProductImage]:
        """
        Получить список изображений продукта по идентификатору продукта.
        """
        logger.info("Fetching product images for product_id %s", product_id)
        query = select(ProductImage).where(ProductImage.product_id == product_id).order_by(ProductImage.id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def ensure_single_main_for_product(self, product_id: int, main_image_id: int) -> None:
        """
        Сделать главным только одно изображение продукта; у остальных сбросить is_main.
        """
        await self.session.execute(
            update(ProductImage).where(ProductImage.product_id == product_id).values(is_main=False)
        )
        await self.session.execute(
            update(ProductImage).where(ProductImage.id == main_image_id).values(is_main=True)
        )
        await self.session.commit()

    async def delete_all_by_product_id(self, product_id: int) -> None:
        """Удалить все изображения продукта."""
        await self.session.execute(delete(ProductImage).where(ProductImage.product_id == product_id))
        await self.session.commit()

    async def set_product_images(
        self, product_id: int, image_urls: List[str], main_index: Optional[int] = None
    ) -> List[ProductImage]:
        """
        Заменить изображения продукта на новый список.
        main_index — порядковый номер (1-based). Если не задан или некорректен — главным первое.
        """
        await self.delete_all_by_product_id(product_id)
        urls_clean = [(u or "").strip() for u in image_urls if (u or "").strip()]
        if not urls_clean:
            return []
        n = len(urls_clean)
        effective = main_index if (main_index is not None and 1 <= main_index <= n) else 1
        main_zero = effective - 1
        created = []
        for i, url in enumerate(urls_clean):
            img = ProductImage(
                product_id=product_id,
                image_url=url,
                is_main=(i == main_zero),
            )
            self.session.add(img)
            created.append(img)
        await self.session.commit()
        for img in created:
            await self.session.refresh(img)
        if len(created) > 1:
            main_id = created[main_zero].id
            await self.ensure_single_main_for_product(product_id, main_id)
        return created

    async def add_product_images(
        self, product_id: int, image_urls: List[str], main_index: Optional[int] = None
    ) -> List[ProductImage]:
        """
        Добавить изображения к продукту (не удаляя существующие).
        main_index — порядковый номер среди новых (1-based); если задан, это новое изображение станет главным.
        """
        urls_clean = [(u or "").strip() for u in image_urls if (u or "").strip()]
        if not urls_clean:
            return []
        existing = await self.get_product_images_by_product_id(product_id)
        n = len(urls_clean)
        effective = main_index if (main_index is not None and 1 <= main_index <= n) else None
        main_zero = (effective - 1) if effective else None
        created = []
        for i, url in enumerate(urls_clean):
            is_main = False
            if len(existing) == 0 and i == 0:
                is_main = True
            elif main_zero is not None and i == main_zero:
                is_main = True
            img = ProductImage(
                product_id=product_id,
                image_url=url,
                is_main=is_main,
            )
            self.session.add(img)
            created.append(img)
        await self.session.commit()
        for img in created:
            await self.session.refresh(img)
        if any(img.is_main for img in created):
            main_id = next(img.id for img in created if img.is_main)
            await self.ensure_single_main_for_product(product_id, main_id)
        return created

    async def create_product_image(self, request: ProductImageCreateRequest) -> ProductImage:
        """
        Создать новое изображение продукта.
        Гарантирует, что только одно изображение продукта имеет is_main=True:
        - если у продукта ещё нет изображений — новое делаем главным;
        - если у нового is_main=True — у остальных изображений продукта сбрасываем is_main.
        """
        logger.info("Creating product image for product_id %s", request.product_id)
        existing = await self.get_product_images_by_product_id(request.product_id)
        is_main = request.is_main if request.is_main is not None else False
        if len(existing) == 0:
            is_main = True

        product_image = ProductImage(
            product_id=request.product_id,
            image_url=request.image_url,
            is_main=is_main,
        )

        self.session.add(product_image)
        await self.session.commit()
        await self.session.refresh(product_image)

        if is_main and existing:
            await self.ensure_single_main_for_product(request.product_id, product_image.id)

        logger.info("Product image created with id %s", product_image.id)
        return product_image

    async def delete_product_image(self, product_image_id: int) -> bool:
        """
        Удалить изображение продукта по идентификатору.
        Если удаляется главное изображение (is_main=True), главным делается первое из оставшихся.
        """
        logger.info("Deleting product image with id %s", product_image_id)
        product_image = await self.get_product_image_by_id(product_image_id)
        if product_image is None:
            logger.warning("Product image with id %s not found for deletion", product_image_id)
            return False

        product_id = product_image.product_id
        was_main = product_image.is_main

        await self.session.delete(product_image)
        await self.session.commit()

        if was_main:
            remaining = await self.get_product_images_by_product_id(product_id)
            if remaining:
                await self.ensure_single_main_for_product(product_id, remaining[0].id)

        logger.info("Product image with id %s successfully deleted", product_image_id)
        return True


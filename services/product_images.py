import logging

from fastapi import HTTPException, status

from repositories.product_images import ProductImageRepository
from core.schemas.product_images import (
    ProductImageCreateRequest,
    ProductImagesSetRequest,
    ProductImageResponse,
    ProductImageListResponse,
    ProductImageDeleteResponse,
)

logger = logging.getLogger(__name__)


class ProductImageService:
    def __init__(self, repository: ProductImageRepository):
        self.repository = repository

    async def get_all_product_images(self) -> ProductImageListResponse:
        """
        Получить список всех изображений продуктов.
        """
        logger.info("Fetching all product images via service")
        product_images = await self.repository.get_all_product_images()
        items = [
            ProductImageResponse(
                id=pi.id,
                product_id=pi.product_id,
                image_url=pi.image_url,
                is_main=pi.is_main,
                message=None,
            )
            for pi in product_images
        ]

        response = ProductImageListResponse(
            items=items,
            message="Список изображений продуктов успешно получен",
        )
        logger.info("Successfully fetched %d product images", len(items))
        return response

    async def get_product_image_by_id(self, product_image_id: int) -> ProductImageResponse:
        """
        Получить изображение продукта по идентификатору.
        """
        logger.info("Fetching product image by id: %s via service", product_image_id)
        product_image = await self.repository.get_product_image_by_id(product_image_id)
        if not product_image:
            logger.error("Product image with id %s not found", product_image_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Изображение продукта с id {product_image_id} не найдено",
            )

        response = ProductImageResponse(
            id=product_image.id,
            product_id=product_image.product_id,
            image_url=product_image.image_url,
            is_main=product_image.is_main,
            message="Изображение продукта успешно найдено",
        )
        logger.info("Product image with id %s successfully retrieved", product_image_id)
        return response

    async def create_product_image(
        self,
        request: ProductImageCreateRequest,
    ) -> ProductImageResponse:
        """
        Создать новое изображение продукта.
        """
        logger.info("Creating product image via service for product_id %s", request.product_id)

        if not request.image_url or len(request.image_url.strip()) == 0:
            logger.error("Product image image_url is empty")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL изображения обязателен для заполнения",
            )

        product_image = await self.repository.create_product_image(request)

        response = ProductImageResponse(
            id=product_image.id,
            product_id=product_image.product_id,
            image_url=product_image.image_url,
            is_main=product_image.is_main,
            message="Изображение продукта успешно создано",
        )
        logger.info("Product image created with id %s via service", product_image.id)
        return response

    async def set_product_images(self, request: ProductImagesSetRequest) -> ProductImageListResponse:
        """
        Заменить изображения продукта на переданный список ссылок.
        main_index — порядковый номер (1-based). Не задан или некорректен → главным первое.
        """
        logger.info("Setting product images via service for product_id %s", request.product_id)
        image_urls = request.image_urls or []
        product_images = await self.repository.set_product_images(
            request.product_id, image_urls, request.main_index
        )
        items = [
            ProductImageResponse(
                id=pi.id,
                product_id=pi.product_id,
                image_url=pi.image_url,
                is_main=pi.is_main,
                message=None,
            )
            for pi in product_images
        ]
        return ProductImageListResponse(
            items=items,
            message=f"Изображения продукта обновлены: {len(items)} шт.",
        )

    async def delete_product_image(self, product_image_id: int) -> ProductImageDeleteResponse:
        """
        Удалить изображение продукта по идентификатору.
        """
        logger.info("Deleting product image via service with id %s", product_image_id)
        success = await self.repository.delete_product_image(product_image_id)
        if not success:
            logger.error("Product image with id %s not found for deletion", product_image_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Изображение продукта с id {product_image_id} не найдено",
            )

        response = ProductImageDeleteResponse(
            product_image_id=product_image_id,
            message="Изображение продукта успешно удалено",
        )
        logger.info("Product image with id %s successfully deleted via service", product_image_id)
        return response


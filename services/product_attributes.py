import logging

from fastapi import HTTPException, status

from repositories.product_attributes import ProductAttributeRepository
from core.schemas.product_attributes import (
    ProductAttributeCreateRequest,
    ProductAttributeUpdateRequest,
    ProductAttributeResponse,
    ProductAttributeListResponse,
)

logger = logging.getLogger(__name__)


class ProductAttributeService:
    def __init__(self, repository: ProductAttributeRepository):
        self.repository = repository

    async def get_all_product_attributes(self) -> ProductAttributeListResponse:
        """
        Получить список всех атрибутов продуктов.
        """
        logger.info("Fetching all product attributes via service")
        product_attributes = await self.repository.get_all_product_attributes()
        items = [
            ProductAttributeResponse(
                product_id=pa.product_id,
                attribute_id=pa.attribute_id,
                value=pa.value,
                message=None,
            )
            for pa in product_attributes
        ]

        response = ProductAttributeListResponse(
            items=items,
            message="Список атрибутов продуктов успешно получен",
        )
        logger.info("Successfully fetched %d product attributes", len(items))
        return response

    async def get_product_attribute_by_id(
        self, product_id: int, attribute_id: int
    ) -> ProductAttributeResponse:
        """
        Получить атрибут продукта по идентификаторам.
        """
        logger.info("Fetching product attribute by product_id: %s and attribute_id: %s via service", product_id, attribute_id)
        product_attribute = await self.repository.get_product_attribute_by_id(product_id, attribute_id)
        if not product_attribute:
            logger.error("Product attribute with product_id %s and attribute_id %s not found", product_id, attribute_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Атрибут продукта с product_id {product_id} и attribute_id {attribute_id} не найден",
            )

        response = ProductAttributeResponse(
            product_id=product_attribute.product_id,
            attribute_id=product_attribute.attribute_id,
            value=product_attribute.value,
            message="Атрибут продукта успешно найден",
        )
        logger.info("Product attribute with product_id %s and attribute_id %s successfully retrieved", product_id, attribute_id)
        return response

    async def create_product_attribute(
        self,
        request: ProductAttributeCreateRequest,
    ) -> ProductAttributeResponse:
        """
        Создать новый атрибут продукта.
        """
        logger.info("Creating product attribute via service for product_id %s and attribute_id %s", request.product_id, request.attribute_id)

        if len(request.value.strip()) < 1:
            logger.error("Product attribute value too short: '%s'", request.value)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Значение атрибута не может быть пустым",
            )

        # Проверяем, не существует ли уже такой атрибут продукта
        existing = await self.repository.get_product_attribute_by_id(request.product_id, request.attribute_id)
        if existing:
            logger.error("Product attribute with product_id %s and attribute_id %s already exists", request.product_id, request.attribute_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Атрибут продукта с product_id {request.product_id} и attribute_id {request.attribute_id} уже существует",
            )

        product_attribute = await self.repository.create_product_attribute(request)

        response = ProductAttributeResponse(
            product_id=product_attribute.product_id,
            attribute_id=product_attribute.attribute_id,
            value=product_attribute.value,
            message="Атрибут продукта успешно создан",
        )
        logger.info("Product attribute created for product_id %s and attribute_id %s via service", product_attribute.product_id, product_attribute.attribute_id)
        return response

    async def update_product_attribute(
        self,
        product_id: int,
        attribute_id: int,
        request: ProductAttributeUpdateRequest,
    ) -> ProductAttributeResponse:
        """
        Обновить атрибут продукта по идентификаторам.
        """
        logger.info("Updating product attribute via service with product_id %s and attribute_id %s", product_id, attribute_id)

        if len(request.value.strip()) < 1:
            logger.error("Product attribute value too short: '%s'", request.value)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Значение атрибута не может быть пустым",
            )

        product_attribute = await self.repository.update_product_attribute(product_id, attribute_id, request)
        if not product_attribute:
            logger.error("Product attribute with product_id %s and attribute_id %s not found for update", product_id, attribute_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Атрибут продукта с product_id {product_id} и attribute_id {attribute_id} не найден",
            )

        response = ProductAttributeResponse(
            product_id=product_attribute.product_id,
            attribute_id=product_attribute.attribute_id,
            value=product_attribute.value,
            message="Атрибут продукта успешно обновлен",
        )
        logger.info("Product attribute with product_id %s and attribute_id %s successfully updated via service", product_id, attribute_id)
        return response


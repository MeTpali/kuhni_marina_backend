import logging
from typing import List
from math import ceil

from fastapi import HTTPException, status

from repositories.products import ProductRepository
from core.models.products import ProductType
from core.schemas.products import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductListItemResponse,
    ProductCatalogResponse,
    ProductIdListResponse,
    ProductListResponse,
    ProductDeleteResponse,
    ProductAttributeResponse,
    ProductImageResponse,
)
from core.schemas.categories import CategoryResponse

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    async def get_product_catalog(
        self,
        page: int = 1,
        page_size: int = 20,
        category_ids: List[int] = None,
        attribute_filters: List[dict] = None,
    ) -> ProductCatalogResponse:
        """
        Получить каталог продуктов с фильтрами и пагинацией.
        """
        logger.info(
            "Service call: get_product_catalog page=%s, page_size=%s, category_ids=%s",
            page,
            page_size,
            category_ids,
        )

        products, total = await self.repository.get_product_catalog(
            page=page,
            page_size=page_size,
            category_ids=category_ids,
            attribute_filters=attribute_filters,
        )

        items = []
        for product in products:
            # Находим главное изображение
            main_image = None
            for img in product.images:
                if img.is_main:
                    main_image = img.image_url
                    break
            if not main_image and product.images:
                main_image = product.images[0].image_url

            items.append(
                ProductListItemResponse(
                    id=product.id,
                    name=product.name,
                    slug=product.slug,
                    category_id=product.category_id,
                    category_name=product.category.name if product.category else None,
                    price=product.price,
                    is_new=product.is_new,
                    is_hit=product.is_hit,
                    type=ProductType(product.type) if isinstance(product.type, str) else product.type,
                    main_image=main_image,
                    is_active=product.is_active,
                )
            )

        total_pages = ceil(total / page_size) if page_size > 0 else 0

        response = ProductCatalogResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            message="Каталог продуктов успешно получен",
        )
        logger.info("Service: fetched %d products (total: %d)", len(items), total)
        return response

    async def get_product_ids(
        self,
        category_ids: List[int] = None,
        attribute_filters: List[dict] = None,
    ) -> ProductIdListResponse:
        """
        Получить список ID продуктов с фильтрами.
        """
        logger.info(
            "Service call: get_product_ids category_ids=%s, attribute_filters=%s",
            category_ids,
            attribute_filters,
        )

        product_ids = await self.repository.get_product_ids(
            category_ids=category_ids,
            attribute_filters=attribute_filters,
        )

        response = ProductIdListResponse(
            product_ids=list(product_ids),
            total=len(product_ids),
            message="Список ID продуктов успешно получен",
        )
        logger.info("Service: fetched %d product IDs", len(product_ids))
        return response

    async def get_product_by_id(self, product_id: int) -> ProductResponse:
        """
        Получить продукт по идентификатору с категорией, атрибутами и изображениями.
        """
        logger.info("Service call: get_product_by_id %s", product_id)
        product = await self.repository.get_product_by_id(product_id)
        if not product:
            logger.error("Product %s not found", product_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Продукт с id {product_id} не найден",
            )

        # Формируем ответ с вложенными объектами
        category_response = None
        if product.category:
            category_response = CategoryResponse(
                id=product.category.id,
                name=product.category.name,
                slug=product.category.slug,
                parent_id=product.category.parent_id,
                type=product.category.type,
                is_active=product.category.is_active,
                message=None,
            )

        attributes_response = []
        if product.attributes:
            for pa in product.attributes:
                attributes_response.append(
                    ProductAttributeResponse(
                        attribute_id=pa.attribute_id,
                        attribute_name=pa.attribute.name if pa.attribute else "",
                        attribute_unit=pa.attribute.unit if pa.attribute else None,
                        value=pa.value,
                    )
                )

        images_response = []
        if product.images:
            for img in product.images:
                images_response.append(
                    ProductImageResponse(
                        id=img.id,
                        image_url=img.image_url,
                        is_main=img.is_main,
                    )
                )

        response = ProductResponse(
            id=product.id,
            name=product.name,
            slug=product.slug,
            category_id=product.category_id,
            description=product.description,
            price=product.price,
            is_new=product.is_new,
            is_hit=product.is_hit,
            type=ProductType(product.type) if isinstance(product.type, str) else product.type,
            category=category_response,
            attributes=attributes_response,
            images=images_response,
            is_active=product.is_active,
            created_at=product.created_at.isoformat() if product.created_at else None,
            updated_at=product.updated_at.isoformat() if product.updated_at else None,
            message="Продукт успешно найден",
        )
        logger.info("Service: product %s retrieved", product_id)
        return response

    async def create_product(self, request: ProductCreateRequest) -> ProductResponse:
        """
        Создать новый продукт.
        """
        logger.info("Service call: create_product name=%s", request.name)

        # Валидация категории
        from repositories.categories import CategoryRepository
        from db.session import get_async_session
        from sqlalchemy.ext.asyncio import AsyncSession

        # Получаем сессию из репозитория
        category_repo = CategoryRepository(self.repository.session)
        category = await category_repo.get_category_by_id(request.category_id)
        if not category:
            logger.error("Category %s not found", request.category_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория с id {request.category_id} не найдена",
            )

        product = await self.repository.create_product(request)

        # Формируем ответ
        category_response = CategoryResponse(
            id=category.id,
            name=category.name,
            slug=category.slug,
            parent_id=category.parent_id,
            type=category.type,
            is_active=category.is_active,
            message=None,
        )

        attributes_response = []
        if product.attributes:
            for pa in product.attributes:
                await self.repository.session.refresh(pa, ["attribute"])
                attributes_response.append(
                    ProductAttributeResponse(
                        attribute_id=pa.attribute_id,
                        attribute_name=pa.attribute.name if pa.attribute else "",
                        attribute_unit=pa.attribute.unit if pa.attribute else None,
                        value=pa.value,
                    )
                )

        images_response = []
        if product.images:
            for img in product.images:
                images_response.append(
                    ProductImageResponse(
                        id=img.id,
                        image_url=img.image_url,
                        is_main=img.is_main,
                    )
                )

        response = ProductResponse(
            id=product.id,
            name=product.name,
            slug=product.slug,
            category_id=product.category_id,
            description=product.description,
            price=product.price,
            is_new=product.is_new,
            is_hit=product.is_hit,
            type=ProductType(product.type) if isinstance(product.type, str) else product.type,
            category=category_response,
            attributes=attributes_response,
            images=images_response,
            is_active=product.is_active,
            created_at=product.created_at.isoformat() if product.created_at else None,
            updated_at=product.updated_at.isoformat() if product.updated_at else None,
            message="Продукт успешно создан",
        )
        logger.info("Service: product %s created", product.id)
        return response

    async def update_product(
        self, product_id: int, request: ProductUpdateRequest
    ) -> ProductResponse:
        """
        Обновить продукт по идентификатору.
        """
        logger.info("Service call: update_product %s", product_id)

        # Валидация категории, если указана
        if request.category_id is not None:
            from repositories.categories import CategoryRepository

            category_repo = CategoryRepository(self.repository.session)
            category = await category_repo.get_category_by_id(request.category_id)
            if not category:
                logger.error("Category %s not found", request.category_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Категория с id {request.category_id} не найдена",
                )

        product = await self.repository.update_product(product_id, request)
        if not product:
            logger.error("Product %s not found for update", product_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Продукт с id {product_id} не найден",
            )

        # Формируем ответ
        category_response = None
        if product.category:
            category_response = CategoryResponse(
                id=product.category.id,
                name=product.category.name,
                slug=product.category.slug,
                parent_id=product.category.parent_id,
                type=product.category.type,
                is_active=product.category.is_active,
                message=None,
            )

        attributes_response = []
        if product.attributes:
            for pa in product.attributes:
                await self.repository.session.refresh(pa, ["attribute"])
                attributes_response.append(
                    ProductAttributeResponse(
                        attribute_id=pa.attribute_id,
                        attribute_name=pa.attribute.name if pa.attribute else "",
                        attribute_unit=pa.attribute.unit if pa.attribute else None,
                        value=pa.value,
                    )
                )

        images_response = []
        if product.images:
            for img in product.images:
                images_response.append(
                    ProductImageResponse(
                        id=img.id,
                        image_url=img.image_url,
                        is_main=img.is_main,
                    )
                )

        response = ProductResponse(
            id=product.id,
            name=product.name,
            slug=product.slug,
            category_id=product.category_id,
            description=product.description,
            price=product.price,
            is_new=product.is_new,
            is_hit=product.is_hit,
            type=ProductType(product.type) if isinstance(product.type, str) else product.type,
            category=category_response,
            attributes=attributes_response,
            images=images_response,
            is_active=product.is_active,
            created_at=product.created_at.isoformat() if product.created_at else None,
            updated_at=product.updated_at.isoformat() if product.updated_at else None,
            message="Продукт успешно обновлен",
        )
        logger.info("Service: product %s updated", product_id)
        return response

    async def delete_product(self, product_id: int) -> ProductDeleteResponse:
        """
        Удалить продукт (деактивировать).
        """
        logger.info("Service call: delete_product %s", product_id)
        success = await self.repository.deactivate_product(product_id)
        if not success:
            logger.error("Product %s not found for deletion", product_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Продукт с id {product_id} не найден",
            )

        response = ProductDeleteResponse(
            product_id=product_id,
            message="Продукт успешно деактивирован",
        )
        logger.info("Service: product %s deactivated", product_id)
        return response

import logging
from typing import List, Optional
from math import ceil
from decimal import Decimal

from fastapi import HTTPException, status

from repositories.products import ProductRepository
from repositories.categories import CategoryRepository
from repositories.discounts import DiscountRepository
from repositories.reviews import ReviewRepository
from core.models.products import ProductType
from core.models.categories import CategoryType
from core.models.discounts import DiscountType
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
    ProductDiscountInfo,
    ProductSuggestionItemResponse,
    ProductSearchSuggestionsResponse,
    CatalogFacets,
    CategoryFacetTreeNode,
    AttributeFacetItem,
    AttributeFacetValue,
)
from core.schemas.categories import CategoryResponse

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def _calculate_discount_info(
        self,
        price: Optional[Decimal],
        discount_value: Decimal,
        discount_type: DiscountType,
    ) -> Optional[ProductDiscountInfo]:
        """
        Вычислить информацию о скидке для продукта.
        """
        if price is None or price <= 0:
            return None

        # Убеждаемся, что discount_value это Decimal
        if not isinstance(discount_value, Decimal):
            discount_value = Decimal(str(discount_value))

        # Убеждаемся, что discount_type это Enum
        if isinstance(discount_type, str):
            discount_type = DiscountType(discount_type)

        if discount_type == DiscountType.PERCENTAGE:
            # Процентная скидка
            discount_percent = discount_value
            discount_amount = price * (discount_value / Decimal(100))
            final_price = price - discount_amount
        else:
            # Фиксированная скидка
            discount_percent = (discount_value / price) * Decimal(100) if price > 0 else Decimal(0)
            discount_amount = min(discount_value, price)  # Скидка не может быть больше цены
            final_price = price - discount_amount

        # Убеждаемся, что итоговая цена не отрицательная
        if final_price < 0:
            final_price = Decimal(0)
            discount_amount = price

        return ProductDiscountInfo(
            discount_percent=round(discount_percent, 2),
            discount_amount=round(discount_amount, 2),
            final_price=round(final_price, 2),
        )

    async def _get_product_discount(
        self,
        product_id: int,
        category_id: int,
        product_type: ProductType,
        price: Optional[Decimal],
    ) -> Optional[ProductDiscountInfo]:
        """
        Получить информацию о скидке для продукта.
        """
        if price is None or price <= 0:
            return None

        discount_repo = DiscountRepository(self.repository.session)
        discount = await discount_repo.get_active_discount_for_product(
            product_id=product_id,
            category_id=category_id,
            product_type=product_type,
        )

        if discount is None:
            return None

        return self._calculate_discount_info(price, discount.value, discount.discount_type)

    @staticmethod
    def _truncate_description(description: Optional[str], max_length: int = 150) -> Optional[str]:
        """Обрезать описание до max_length символов с '...' в конце."""
        if not description or not description.strip():
            return None
        s = description.strip()
        if len(s) <= max_length:
            return s
        return s[:max_length].rstrip() + "..."

    @staticmethod
    def _build_category_facet_tree(
        categories_flat: list,
        facet_count_by_id: dict,
    ) -> List[CategoryFacetTreeNode]:
        """
        Строит дерево категорий для фасета. В каждом узле count = прямые товары этой категории;
        после агрегации у родителя count += сумма count всех детей (итого у родителя — сумма по поддереву).
        """
        nodes: dict[int, CategoryFacetTreeNode] = {}
        roots: List[CategoryFacetTreeNode] = []

        for cat in categories_flat:
            node = CategoryFacetTreeNode(
                id=cat.id,
                name=cat.name,
                slug=cat.slug,
                count=facet_count_by_id.get(cat.id, 0),
                children=[],
            )
            nodes[cat.id] = node

        for cat in categories_flat:
            node = nodes[cat.id]
            parent_id = getattr(cat, "parent_id", None)
            if parent_id and parent_id in nodes:
                nodes[parent_id].children.append(node)
            else:
                roots.append(node)

        def aggregate_count(node: CategoryFacetTreeNode) -> None:
            for child in node.children:
                aggregate_count(child)
            node.count += sum(c.count for c in node.children)

        for root in roots:
            aggregate_count(root)

        return roots

    async def get_product_catalog(
        self,
        page: int = 1,
        page_size: int = 20,
        category_ids: List[int] = None,
        attribute_filters: List[dict] = None,
        is_hit: Optional[bool] = None,
        is_new: Optional[bool] = None,
        has_discount: Optional[bool] = None,
        campaign_id: Optional[int] = None,
        product_type: Optional[ProductType] = None,
        search_query: Optional[str] = None,
    ) -> ProductCatalogResponse:
        """
        Получить каталог продуктов с фильтрами и пагинацией.
        """
        logger.info(
            "Service call: get_product_catalog page=%s, page_size=%s, category_ids=%s, is_hit=%s, is_new=%s, has_discount=%s, product_type=%s, search_query=%s",
            page,
            page_size,
            category_ids,
            is_hit,
            is_new,
            has_discount,
            product_type,
            search_query,
        )

        products, total = await self.repository.get_product_catalog(
            page=page,
            page_size=page_size,
            category_ids=category_ids,
            attribute_filters=attribute_filters,
            is_hit=is_hit,
            is_new=is_new,
            has_discount=has_discount,
            campaign_id=campaign_id,
            product_type=product_type,
            search_query=search_query,
        )

        # Фасеты: категории (дерево с count = сумма по себе и потомкам), атрибуты (без attribute_filters)
        category_facet_rows = await self.repository.get_catalog_category_facets(
            is_hit=is_hit,
            is_new=is_new,
            has_discount=has_discount,
            campaign_id=campaign_id,
            product_type=product_type,
            search_query=search_query,
        )
        attribute_facet_rows = await self.repository.get_catalog_attribute_facets(
            category_ids=category_ids,
            is_hit=is_hit,
            is_new=is_new,
            has_discount=has_discount,
            campaign_id=campaign_id,
            product_type=product_type,
            search_query=search_query,
        )

        # Прямые счётчики по category_id (товары с этой категорией)
        facet_count_by_id = {cat_id: count for cat_id, _name, _slug, count in category_facet_rows}

        # Дерево категорий: берём по типу продукта или все
        category_repo = CategoryRepository(self.repository.session)
        if product_type is not None:
            cat_type = CategoryType(product_type.value) if hasattr(product_type, "value") else product_type
            categories_flat = await category_repo.get_categories_by_type(cat_type)
        else:
            categories_flat = await category_repo.get_all_categories()

        categories_facet = self._build_category_facet_tree(categories_flat, facet_count_by_id)
        # Группируем атрибуты по attribute_id
        attr_map: dict = {}
        for attr_id, attr_name, unit, value, count in attribute_facet_rows:
            if attr_id not in attr_map:
                attr_map[attr_id] = AttributeFacetItem(
                    attribute_id=attr_id,
                    attribute_name=attr_name,
                    unit=unit,
                    values=[],
                )
            attr_map[attr_id].values.append(AttributeFacetValue(value=value, count=count))
        attributes_facet = list(attr_map.values())

        facets = CatalogFacets(categories=categories_facet, attributes=attributes_facet)

        product_ids = [p.id for p in products]
        review_repo = ReviewRepository(self.repository.session)
        review_stats = await review_repo.get_approved_review_stats_by_product_ids(product_ids)

        items = []
        for product in products:
            # Список URL изображений: первым — главное (is_main), остальные по порядку
            sorted_images = sorted(
                product.images,
                key=lambda img: (0 if img.is_main else 1),
            )
            images = [img.image_url for img in sorted_images]

            # Вычисляем скидку
            discount = await self._get_product_discount(
                product_id=product.id,
                category_id=product.category_id,
                product_type=ProductType(product.type) if isinstance(product.type, str) else product.type,
                price=product.price,
            )

            rating, reviews_count = review_stats.get(product.id, (0.0, 0))
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
                    images=images,
                    is_active=product.is_active,
                    discount=discount,
                    rating=rating,
                    reviews_count=reviews_count,
                )
            )

        total_pages = ceil(total / page_size) if page_size > 0 else 0

        response = ProductCatalogResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            facets=facets,
            message="Каталог продуктов успешно получен",
        )
        logger.info("Service: fetched %d products (total: %d)", len(items), total)
        return response

    async def get_catalog_hits(
        self,
        page: int = 1,
        page_size: int = 20,
        category_ids: List[int] = None,
        attribute_filters: List[dict] = None,
        product_type: Optional[ProductType] = None,
    ) -> ProductCatalogResponse:
        """Получить каталог продуктов-хитов с пагинацией."""
        return await self.get_product_catalog(
            page=page,
            page_size=page_size,
            category_ids=category_ids,
            attribute_filters=attribute_filters,
            is_hit=True,
            product_type=product_type,
        )

    async def get_catalog_new(
        self,
        page: int = 1,
        page_size: int = 20,
        category_ids: List[int] = None,
        attribute_filters: List[dict] = None,
        product_type: Optional[ProductType] = None,
    ) -> ProductCatalogResponse:
        """Получить каталог новинок с пагинацией."""
        return await self.get_product_catalog(
            page=page,
            page_size=page_size,
            category_ids=category_ids,
            attribute_filters=attribute_filters,
            is_new=True,
            product_type=product_type,
        )

    async def get_catalog_discounts(
        self,
        page: int = 1,
        page_size: int = 20,
        category_ids: List[int] = None,
        attribute_filters: List[dict] = None,
        product_type: Optional[ProductType] = None,
    ) -> ProductCatalogResponse:
        """Получить каталог продуктов со скидкой с пагинацией."""
        return await self.get_product_catalog(
            page=page,
            page_size=page_size,
            category_ids=category_ids,
            attribute_filters=attribute_filters,
            has_discount=True,
            product_type=product_type,
        )

    async def get_search_suggestions(
        self,
        text: str,
        product_type: Optional[ProductType] = None,
        limit: int = 10,
    ) -> ProductSearchSuggestionsResponse:
        """
        Подсказки поиска для автодополнения: id, картинка (опционально),
        описание не более 150 символов с троеточием, цена, скидка (опционально).
        """
        products = await self.repository.get_product_search_suggestions(
            search_query=text,
            product_type=product_type,
            limit=limit,
        )
        items = []
        for product in products:
            main_image = None
            for img in product.images:
                if img.is_main:
                    main_image = img.image_url
                    break
            if not main_image and product.images:
                main_image = product.images[0].image_url

            discount = await self._get_product_discount(
                product_id=product.id,
                category_id=product.category_id,
                product_type=ProductType(product.type) if isinstance(product.type, str) else product.type,
                price=product.price,
            )

            items.append(
                ProductSuggestionItemResponse(
                    id=product.id,
                    name=product.name,
                    image=main_image,
                    description=self._truncate_description(product.description),
                    price=product.price,
                    discount=discount,
                )
            )
        return ProductSearchSuggestionsResponse(
            items=items,
            message="Подсказки поиска получены",
        )

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

        # Вычисляем скидку
        discount = await self._get_product_discount(
            product_id=product.id,
            category_id=product.category_id,
            product_type=ProductType(product.type) if isinstance(product.type, str) else product.type,
            price=product.price,
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
            discount=discount,
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

        # Вычисляем скидку
        discount = await self._get_product_discount(
            product_id=product.id,
            category_id=product.category_id,
            product_type=ProductType(product.type) if isinstance(product.type, str) else product.type,
            price=product.price,
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
            discount=discount,
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

        # Вычисляем скидку
        discount = await self._get_product_discount(
            product_id=product.id,
            category_id=product.category_id,
            product_type=ProductType(product.type) if isinstance(product.type, str) else product.type,
            price=product.price,
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
            discount=discount,
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

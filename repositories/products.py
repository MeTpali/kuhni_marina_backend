from typing import List, Optional, Tuple
import logging
from datetime import datetime

from sqlalchemy import select, func, and_, or_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models.products import Product, ProductType
from core.models.product_images import ProductImage
from core.models.product_attributes import ProductAttribute
from core.models.categories import Category
from core.models.attributes import Attribute
from core.models.discounts import Discount, DiscountScope
from core.schemas.products import ProductCreateRequest, ProductUpdateRequest
from core.utils.slug import generate_unique_slug

logger = logging.getLogger(__name__)


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_product_catalog(
        self,
        page: int = 1,
        page_size: int = 20,
        category_ids: Optional[List[int]] = None,
        attribute_filters: Optional[List[dict]] = None,  # [{"attribute_id": int, "value": str}]
        include_inactive: bool = False,
        is_hit: Optional[bool] = None,
        is_new: Optional[bool] = None,
        has_discount: Optional[bool] = None,
        product_type: Optional[ProductType] = None,
        search_query: Optional[str] = None,
    ) -> Tuple[List[Product], int]:
        """
        Получить каталог продуктов с фильтрами и пагинацией.
        Возвращает список продуктов и общее количество.
        """
        logger.info(
            "Fetching product catalog: page=%s, page_size=%s, category_ids=%s, attribute_filters=%s, is_hit=%s, is_new=%s, has_discount=%s, product_type=%s, search_query=%s",
            page,
            page_size,
            category_ids,
            attribute_filters,
            is_hit,
            is_new,
            has_discount,
            product_type,
            search_query,
        )

        # Базовый запрос
        query = select(Product).options(
            selectinload(Product.category),
            selectinload(Product.images),
        )
        query = self._apply_catalog_filters(
            query,
            category_ids=category_ids,
            attribute_filters=attribute_filters,
            include_inactive=include_inactive,
            is_hit=is_hit,
            is_new=is_new,
            has_discount=has_discount,
            product_type=product_type,
            search_query=search_query,
            apply_category_filter=True,
            apply_attribute_filter=True,
        )

        # Подсчет общего количества
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Применяем пагинацию
        offset = (page - 1) * page_size
        query = query.order_by(Product.id).offset(offset).limit(page_size)

        result = await self.session.execute(query)
        products = result.scalars().unique().all()

        logger.info("Retrieved %d products (total: %d)", len(products), total)
        return products, total

    def _apply_catalog_filters(
        self,
        query,
        *,
        category_ids: Optional[List[int]] = None,
        attribute_filters: Optional[List[dict]] = None,
        include_inactive: bool = False,
        is_hit: Optional[bool] = None,
        is_new: Optional[bool] = None,
        has_discount: Optional[bool] = None,
        product_type: Optional[ProductType] = None,
        search_query: Optional[str] = None,
        apply_category_filter: bool = True,
        apply_attribute_filter: bool = True,
    ):
        """Применить фильтры каталога к запросу. Флаги apply_* позволяют исключить категории/атрибуты для фасетов."""
        if not include_inactive:
            query = query.where(Product.is_active.is_(True))
        if apply_category_filter and category_ids:
            query = query.where(Product.category_id.in_(category_ids))
        if is_hit is not None:
            query = query.where(Product.is_hit.is_(is_hit))
        if is_new is not None:
            query = query.where(Product.is_new.is_(is_new))
        if has_discount is not None:
            now = datetime.now()
            discount_exists = exists().where(
                and_(
                    Discount.is_active.is_(True),
                    Discount.start_date <= now,
                    Discount.end_date >= now,
                    or_(
                        Discount.scope == DiscountScope.ALL,
                        and_(
                            Discount.scope == DiscountScope.PRODUCT,
                            Discount.product_id == Product.id,
                        ),
                        and_(
                            Discount.scope == DiscountScope.CATEGORY,
                            Discount.category_id == Product.category_id,
                        ),
                        and_(
                            Discount.scope == DiscountScope.TYPE,
                            Discount.product_type == Product.type,
                        ),
                    ),
                )
            )
            if has_discount:
                query = query.where(discount_exists)
            else:
                query = query.where(~discount_exists)
        if product_type is not None:
            type_val = product_type.value if hasattr(product_type, "value") else product_type
            query = query.where(Product.type == type_val)
        if search_query and search_query.strip():
            q = f"%{search_query.strip()}%"
            query = query.where(
                or_(
                    Product.name.ilike(q),
                    Product.description.ilike(q),
                )
            )
        if apply_attribute_filter and attribute_filters:
            attribute_conditions = []
            for attr_filter in attribute_filters:
                attr_id = attr_filter.get("attribute_id")
                attr_value = attr_filter.get("value")
                if attr_id and attr_value:
                    subquery = select(ProductAttribute.product_id).where(
                        and_(
                            ProductAttribute.attribute_id == attr_id,
                            ProductAttribute.value == attr_value,
                        )
                    )
                    attribute_conditions.append(Product.id.in_(subquery))
            if attribute_conditions:
                query = query.where(and_(*attribute_conditions))
        return query

    async def get_catalog_category_facets(
        self,
        *,
        include_inactive: bool = False,
        is_hit: Optional[bool] = None,
        is_new: Optional[bool] = None,
        has_discount: Optional[bool] = None,
        product_type: Optional[ProductType] = None,
        search_query: Optional[str] = None,
    ) -> List[Tuple[int, str, str, int]]:
        """
        Фасет категорий: выборка без category_ids и attribute_filters.
        Возвращает список (category_id, name, slug, count).
        При непустом search — только категории из выдачи по поиску.
        """
        query = (
            select(Product.category_id, Category.name, Category.slug, func.count(Product.id).label("cnt"))
            .join(Category, Product.category_id == Category.id)
            .where(Category.is_active.is_(True))
        )
        query = self._apply_catalog_filters(
            query,
            category_ids=None,
            attribute_filters=None,
            include_inactive=include_inactive,
            is_hit=is_hit,
            is_new=is_new,
            has_discount=has_discount,
            product_type=product_type,
            search_query=search_query,
            apply_category_filter=False,
            apply_attribute_filter=False,
        )
        query = query.group_by(Product.category_id, Category.id, Category.name, Category.slug)
        result = await self.session.execute(query)
        rows = result.all()
        return [(r.category_id, r.name, r.slug, r.cnt) for r in rows]

    async def get_catalog_attribute_facets(
        self,
        *,
        category_ids: Optional[List[int]] = None,
        include_inactive: bool = False,
        is_hit: Optional[bool] = None,
        is_new: Optional[bool] = None,
        has_discount: Optional[bool] = None,
        product_type: Optional[ProductType] = None,
        search_query: Optional[str] = None,
    ) -> List[Tuple[int, str, Optional[str], str, int]]:
        """
        Фасет атрибутов: выборка без attribute_filters (category_ids и остальное применяются).
        Возвращает список (attribute_id, attribute_name, unit, value, count).
        """
        # Подзапрос: product_id, удовлетворяющие фильтрам (без атрибутов)
        subq = select(Product.id)
        if not include_inactive:
            subq = subq.where(Product.is_active.is_(True))
        if category_ids:
            subq = subq.where(Product.category_id.in_(category_ids))
        if is_hit is not None:
            subq = subq.where(Product.is_hit.is_(is_hit))
        if is_new is not None:
            subq = subq.where(Product.is_new.is_(is_new))
        if has_discount is not None:
            now = datetime.now()
            discount_exists = exists().where(
                and_(
                    Discount.is_active.is_(True),
                    Discount.start_date <= now,
                    Discount.end_date >= now,
                    or_(
                        Discount.scope == DiscountScope.ALL,
                        and_(Discount.scope == DiscountScope.PRODUCT, Discount.product_id == Product.id),
                        and_(Discount.scope == DiscountScope.CATEGORY, Discount.category_id == Product.category_id),
                        and_(Discount.scope == DiscountScope.TYPE, Discount.product_type == Product.type),
                    ),
                )
            )
            subq = subq.where(discount_exists if has_discount else ~discount_exists)
        if product_type is not None:
            type_val = product_type.value if hasattr(product_type, "value") else product_type
            subq = subq.where(Product.type == type_val)
        if search_query and search_query.strip():
            q = f"%{search_query.strip()}%"
            subq = subq.where(or_(Product.name.ilike(q), Product.description.ilike(q)))
        subq = subq.subquery()

        query = (
            select(
                ProductAttribute.attribute_id,
                Attribute.name.label("attr_name"),
                Attribute.unit,
                ProductAttribute.value,
                func.count(ProductAttribute.product_id.distinct()).label("cnt"),
            )
            .select_from(ProductAttribute)
            .join(Attribute, ProductAttribute.attribute_id == Attribute.id)
            .where(ProductAttribute.product_id.in_(subq))
            .group_by(
                ProductAttribute.attribute_id,
                Attribute.name,
                Attribute.unit,
                ProductAttribute.value,
            )
        )
        result = await self.session.execute(query)
        rows = result.all()
        return [(r.attribute_id, r.attr_name, r.unit, r.value, r.cnt) for r in rows]

    async def get_product_search_suggestions(
        self,
        search_query: str,
        product_type: Optional[ProductType] = None,
        limit: int = 10,
    ) -> List[Product]:
        """
        Получить подсказки поиска: продукты по тексту и опционально типу, с лимитом.
        Для автодополнения в поисковой строке.
        """
        if not search_query or not search_query.strip():
            return []

        q = f"%{search_query.strip()}%"
        query = (
            select(Product)
            .options(
                selectinload(Product.category),
                selectinload(Product.images),
            )
            .where(Product.is_active.is_(True))
            .where(
                or_(
                    Product.name.ilike(q),
                    Product.description.ilike(q),
                )
            )
            .order_by(Product.id)
            .limit(limit)
        )
        if product_type is not None:
            type_val = product_type.value if hasattr(product_type, "value") else product_type
            query = query.where(Product.type == type_val)

        result = await self.session.execute(query)
        products = result.scalars().unique().all()
        logger.info("Retrieved %d search suggestions for query=%s", len(products), search_query[:50])
        return products

    async def get_product_ids(
        self,
        category_ids: Optional[List[int]] = None,
        attribute_filters: Optional[List[dict]] = None,
        include_inactive: bool = False,
    ) -> List[int]:
        """
        Получить список ID продуктов с фильтрами.
        """
        logger.info(
            "Fetching product IDs: category_ids=%s, attribute_filters=%s",
            category_ids,
            attribute_filters,
        )

        query = select(Product.id)

        # Фильтр по активности
        if not include_inactive:
            query = query.where(Product.is_active.is_(True))

        # Фильтр по категориям
        if category_ids:
            query = query.where(Product.category_id.in_(category_ids))

        # Фильтр по атрибутам
        if attribute_filters:
            attribute_conditions = []
            for attr_filter in attribute_filters:
                attr_id = attr_filter.get("attribute_id")
                attr_value = attr_filter.get("value")
                if attr_id and attr_value:
                    subquery = select(ProductAttribute.product_id).where(
                        and_(
                            ProductAttribute.attribute_id == attr_id,
                            ProductAttribute.value == attr_value,
                        )
                    )
                    attribute_conditions.append(Product.id.in_(subquery))

            if attribute_conditions:
                query = query.where(and_(*attribute_conditions))

        result = await self.session.execute(query)
        product_ids = result.scalars().all()

        logger.info("Retrieved %d product IDs", len(product_ids))
        return product_ids

    async def get_product_by_id(
        self, product_id: int, include_inactive: bool = False
    ) -> Optional[Product]:
        """
        Получить продукт по идентификатору с категорией, атрибутами и изображениями.
        """
        logger.info(
            "Fetching product with id %s (include_inactive=%s)", product_id, include_inactive
        )
        query = (
            select(Product)
            .options(
                selectinload(Product.category),
                selectinload(Product.images),
                selectinload(Product.attributes).selectinload(ProductAttribute.attribute),
            )
            .where(Product.id == product_id)
        )
        if not include_inactive:
            query = query.where(Product.is_active.is_(True))
        result = await self.session.execute(query)
        product = result.scalar_one_or_none()
        if product is None:
            logger.warning("Product with id %s not found", product_id)
        return product

    async def generate_unique_slug(self, text: str, exclude_id: Optional[int] = None) -> str:
        """
        Генерирует уникальный slug для продукта.
        """
        return await generate_unique_slug(self.session, Product, text, exclude_id)

    async def create_product(self, request: ProductCreateRequest) -> Product:
        """
        Создать новый продукт.
        """
        logger.info("Creating product with name '%s'", request.name)

        # Генерируем slug, если не передан
        if request.slug is None or not request.slug.strip():
            slug = await self.generate_unique_slug(request.name)
        else:
            slug = await self.generate_unique_slug(request.slug)

        # Создаем продукт
        product = Product(
            name=request.name,
            slug=slug,
            category_id=request.category_id,
            description=request.description,
            price=request.price,
            is_new=request.is_new,
            is_hit=request.is_hit,
            type=request.type.value,  # Используем значение Enum
            is_active=True,
        )

        self.session.add(product)
        await self.session.flush()  # Получаем ID продукта

        # Добавляем изображения
        for img_data in request.images:
            image = ProductImage(
                product_id=product.id,
                image_url=img_data.get("image_url"),
                is_main=img_data.get("is_main", False),
            )
            self.session.add(image)

        # Добавляем атрибуты
        for attr_data in request.attributes:
            attribute = ProductAttribute(
                product_id=product.id,
                attribute_id=attr_data.get("attribute_id"),
                value=attr_data.get("value"),
            )
            self.session.add(attribute)

        await self.session.commit()
        await self.session.refresh(product)

        # Загружаем связанные объекты
        await self.session.refresh(product, ["category", "images", "attributes"])
        if product.attributes:
            for pa in product.attributes:
                await self.session.refresh(pa, ["attribute"])

        logger.info("Product created with id %s", product.id)
        return product

    async def update_product(
        self, product_id: int, request: ProductUpdateRequest
    ) -> Optional[Product]:
        """
        Обновить продукт по идентификатору.
        """
        logger.info("Updating product with id %s", product_id)
        product = await self.get_product_by_id(product_id, include_inactive=True)
        if product is None:
            logger.warning("Product with id %s not found for update", product_id)
            return None

        # Обновляем основные поля
        if request.name is not None:
            product.name = request.name
        if request.slug is not None:
            product.slug = await self.generate_unique_slug(request.slug, exclude_id=product_id)
        elif request.name is not None:
            # Если изменилось имя, но slug не указан, генерируем новый
            product.slug = await self.generate_unique_slug(request.name, exclude_id=product_id)
        if request.category_id is not None:
            product.category_id = request.category_id
        if request.description is not None:
            product.description = request.description
        if request.price is not None:
            product.price = request.price
        if request.is_new is not None:
            product.is_new = request.is_new
        if request.is_hit is not None:
            product.is_hit = request.is_hit
        if request.type is not None:
            product.type = request.type.value if hasattr(request.type, 'value') else request.type

        # Обновляем изображения, если указаны
        if request.images is not None:
            # Удаляем старые изображения
            result = await self.session.execute(
                select(ProductImage).where(ProductImage.product_id == product_id)
            )
            old_images = result.scalars().all()
            for img in old_images:
                await self.session.delete(img)

            # Добавляем новые изображения
            for img_data in request.images:
                image = ProductImage(
                    product_id=product.id,
                    image_url=img_data.get("image_url"),
                    is_main=img_data.get("is_main", False),
                )
                self.session.add(image)

        # Обновляем атрибуты, если указаны
        if request.attributes is not None:
            # Удаляем старые атрибуты
            result = await self.session.execute(
                select(ProductAttribute).where(ProductAttribute.product_id == product_id)
            )
            old_attributes = result.scalars().all()
            for attr in old_attributes:
                await self.session.delete(attr)

            # Добавляем новые атрибуты
            for attr_data in request.attributes:
                attribute = ProductAttribute(
                    product_id=product.id,
                    attribute_id=attr_data.get("attribute_id"),
                    value=attr_data.get("value"),
                )
                self.session.add(attribute)

        await self.session.commit()
        await self.session.refresh(product)

        # Загружаем связанные объекты
        await self.session.refresh(product, ["category", "images", "attributes"])
        if product.attributes:
            for pa in product.attributes:
                await self.session.refresh(pa, ["attribute"])

        logger.info("Product with id %s successfully updated", product_id)
        return product

    async def deactivate_product(self, product_id: int) -> bool:
        """
        Деактивировать продукт (мягкое удаление).
        """
        logger.info("Deactivating product with id %s", product_id)
        product = await self.get_product_by_id(product_id, include_inactive=True)
        if product is None:
            logger.warning("Product with id %s not found for deactivation", product_id)
            return False

        product.is_active = False
        await self.session.commit()

        logger.info("Product with id %s successfully deactivated", product_id)
        return True

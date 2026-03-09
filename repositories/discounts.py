from typing import List, Optional, Tuple
import logging
from datetime import datetime

from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models.discounts import Discount, DiscountType, DiscountScope
from core.models.products import ProductType
from core.schemas.discounts import DiscountCreateRequest, DiscountUpdateRequest

logger = logging.getLogger(__name__)


class DiscountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_discounts(
        self,
        page: int = 1,
        page_size: int = 20,
        include_inactive: bool = False,
        scope: Optional[DiscountScope] = None,
        discount_type: Optional[DiscountType] = None,
        campaign_id: Optional[int] = None,
        product_id: Optional[int] = None,
        category_id: Optional[int] = None,
        product_type: Optional[ProductType] = None,
        is_active: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Tuple[List[Discount], int]:
        """
        Получить список скидок с фильтрацией и сортировкой.
        """
        logger.info(
            "Fetching discounts: page=%s, page_size=%s, include_inactive=%s, scope=%s, discount_type=%s",
            page, page_size, include_inactive, scope, discount_type
        )

        # Базовый запрос
        query = select(Discount).options(
            selectinload(Discount.campaign),
            selectinload(Discount.product),
            selectinload(Discount.category),
        )

        # Подсчет общего количества
        count_query = select(func.count(Discount.id))

        # Применяем фильтры
        conditions = []

        if not include_inactive:
            conditions.append(Discount.is_active.is_(True))

        if scope is not None:
            conditions.append(Discount.scope == scope)

        if discount_type is not None:
            conditions.append(Discount.discount_type == discount_type)

        if campaign_id is not None:
            conditions.append(Discount.campaign_id == campaign_id)

        if product_id is not None:
            conditions.append(Discount.product_id == product_id)

        if category_id is not None:
            conditions.append(Discount.category_id == category_id)

        if product_type is not None:
            conditions.append(Discount.product_type == product_type)

        if is_active is not None:
            conditions.append(Discount.is_active.is_(is_active))

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Сортировка
        if sort_by:
            sort_column = getattr(Discount, sort_by, None)
            if sort_column is not None:
                if sort_order.lower() == "asc":
                    query = query.order_by(asc(sort_column))
                else:
                    query = query.order_by(desc(sort_column))
            else:
                # По умолчанию сортировка по дате создания
                query = query.order_by(desc(Discount.created_at))
        else:
            # По умолчанию сортировка по приоритету и дате создания
            query = query.order_by(desc(Discount.priority), desc(Discount.created_at))

        # Пагинация
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Выполняем запросы
        result = await self.session.execute(query)
        discounts = result.scalars().unique().all()

        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        logger.info("Retrieved %d discounts (total: %d)", len(discounts), total)
        return discounts, total

    async def get_discount_by_id(
        self,
        discount_id: int,
        include_inactive: bool = False,
    ) -> Optional[Discount]:
        """
        Получить скидку по идентификатору.
        """
        logger.info(
            "Fetching discount with id %s (include_inactive=%s)",
            discount_id,
            include_inactive,
        )
        query = (
            select(Discount)
            .options(
                selectinload(Discount.campaign),
                selectinload(Discount.product),
                selectinload(Discount.category),
            )
            .where(Discount.id == discount_id)
        )
        if not include_inactive:
            query = query.where(Discount.is_active.is_(True))

        result = await self.session.execute(query)
        discount = result.scalar_one_or_none()

        if discount is None:
            logger.warning("Discount with id %s not found", discount_id)
        return discount

    async def create_discount(self, request: DiscountCreateRequest) -> Discount:
        """
        Создать новую скидку.
        """
        logger.info("Creating discount with name '%s'", request.name)

        discount = Discount(
            name=request.name,
            discount_type=request.discount_type,
            value=request.value,
            scope=request.scope,
            campaign_id=request.campaign_id,
            product_id=request.product_id,
            category_id=request.category_id,
            product_type=request.product_type,
            start_date=request.start_date,
            end_date=request.end_date,
            is_active=request.is_active,
            priority=request.priority,
        )

        self.session.add(discount)
        await self.session.commit()
        await self.session.refresh(discount)

        logger.info("Discount created with id %s", discount.id)
        return discount

    async def update_discount(
        self,
        discount_id: int,
        request: DiscountUpdateRequest,
    ) -> Optional[Discount]:
        """
        Обновить скидку по идентификатору.
        """
        logger.info("Updating discount with id %s", discount_id)
        discount = await self.get_discount_by_id(discount_id, include_inactive=True)
        if discount is None:
            logger.warning("Discount with id %s not found for update", discount_id)
            return None

        if request.name is not None:
            discount.name = request.name
        if request.discount_type is not None:
            discount.discount_type = request.discount_type
        if request.value is not None:
            discount.value = request.value
        if request.scope is not None:
            discount.scope = request.scope
        if request.campaign_id is not None:
            discount.campaign_id = request.campaign_id
        if request.product_id is not None:
            discount.product_id = request.product_id
        if request.category_id is not None:
            discount.category_id = request.category_id
        if request.product_type is not None:
            discount.product_type = request.product_type
        if request.start_date is not None:
            discount.start_date = request.start_date
        if request.end_date is not None:
            discount.end_date = request.end_date
        if request.is_active is not None:
            discount.is_active = request.is_active
        if request.priority is not None:
            discount.priority = request.priority

        await self.session.commit()
        await self.session.refresh(discount)

        logger.info("Discount with id %s successfully updated", discount_id)
        return discount

    async def deactivate_discount(self, discount_id: int) -> bool:
        """
        Деактивировать скидку по идентификатору (soft delete).
        """
        logger.info("Deactivating discount with id %s", discount_id)
        discount = await self.get_discount_by_id(discount_id, include_inactive=True)
        if discount is None:
            logger.warning("Discount with id %s not found for deactivation", discount_id)
            return False

        discount.is_active = False
        await self.session.commit()

        logger.info("Discount with id %s successfully deactivated", discount_id)
        return True

    async def get_active_discount_for_product(
        self,
        product_id: int,
        category_id: int,
        product_type: ProductType,
        current_date: Optional[datetime] = None,
    ) -> Optional[Discount]:
        """
        Получить активную скидку для продукта.
        Учитывает скидки на продукт, категорию, тип продукта и все продукты.
        Возвращает скидку с наивысшим приоритетом.
        """
        if current_date is None:
            current_date = datetime.now()

        logger.info(
            "Fetching active discount for product_id=%s, category_id=%s, product_type=%s",
            product_id, category_id, product_type
        )

        # Ищем все активные скидки, которые могут применяться к продукту
        query = select(Discount).where(
            and_(
                Discount.is_active.is_(True),
                Discount.start_date <= current_date,
                Discount.end_date >= current_date,
                or_(
                    # Скидка на конкретный продукт
                    and_(Discount.scope == DiscountScope.PRODUCT, Discount.product_id == product_id),
                    # Скидка на категорию
                    and_(Discount.scope == DiscountScope.CATEGORY, Discount.category_id == category_id),
                    # Скидка на тип продукта
                    and_(Discount.scope == DiscountScope.TYPE, Discount.product_type == product_type),
                    # Скидка на все продукты
                    Discount.scope == DiscountScope.ALL,
                )
            )
        ).order_by(
            desc(Discount.priority),
            desc(Discount.created_at),
            desc(Discount.id),  # детерминированный выбор при равных приоритетах/датах
        ).limit(1)

        result = await self.session.execute(query)
        discount = result.scalars().first()

        if discount:
            logger.info("Found active discount %s for product %s (priority: %s)", discount.id, product_id, discount.priority)
        else:
            logger.info("No active discount found for product %s", product_id)

        return discount

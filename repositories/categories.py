from typing import List, Optional
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models.categories import Category, CategoryType
from core.schemas.categories import CategoryCreateRequest, CategoryUpdateRequest
from core.utils.slug import generate_unique_slug

logger = logging.getLogger(__name__)


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_categories(self, include_inactive: bool = False) -> List[Category]:
        logger.info("Fetching all categories (include_inactive=%s)", include_inactive)
        query = select(Category).options(selectinload(Category.children)).order_by(Category.parent_id, Category.id)
        if not include_inactive:
            query = query.where(Category.is_active.is_(True))
        result = await self.session.execute(query)
        categories = result.scalars().unique().all()
        logger.info("Retrieved %d categories", len(categories))
        return categories

    async def get_categories_by_type(
        self,
        category_type: CategoryType,
        include_inactive: bool = False,
    ) -> List[Category]:
        logger.info(
            "Fetching categories by type %s (include_inactive=%s)",
            category_type,
            include_inactive,
        )
        query = (
            select(Category)
            .options(selectinload(Category.children))
            .where(Category.type == category_type)
            .order_by(Category.parent_id, Category.id)
        )
        if not include_inactive:
            query = query.where(Category.is_active.is_(True))
        result = await self.session.execute(query)
        categories = result.scalars().unique().all()
        logger.info("Retrieved %d categories of type %s", len(categories), category_type)
        return categories

    async def get_category_by_id(
        self,
        category_id: int,
        include_inactive: bool = False,
    ) -> Optional[Category]:
        logger.info(
            "Fetching category with id %s (include_inactive=%s)",
            category_id,
            include_inactive,
        )
        query = (
            select(Category)
            .options(selectinload(Category.children))
            .where(Category.id == category_id)
        )
        if not include_inactive:
            query = query.where(Category.is_active.is_(True))
        result = await self.session.execute(query)
        category = result.scalars().unique().one_or_none()
        if category is None:
            logger.warning("Category with id %s not found", category_id)
        return category

    async def generate_unique_slug(self, text: str, exclude_id: Optional[int] = None) -> str:
        """
        Генерирует уникальный slug для категории.
        
        Args:
            text: Исходный текст для генерации slug
            exclude_id: ID категории, которую нужно исключить из проверки (для обновления)
            
        Returns:
            Уникальный slug
        """
        return await generate_unique_slug(self.session, Category, text, exclude_id)

    async def create_category(
        self,
        name: str,
        slug: str,
        category_type: CategoryType,
        parent_id: Optional[int] = None,
        is_active: bool = True,
    ) -> Category:
        logger.info("Creating category with slug '%s', type=%s (value=%s)", slug, category_type, category_type.value)
        # SQLAlchemy должен автоматически использовать .value для Enum,
        # но явно передаем Enum объект, чтобы SQLAlchemy правильно его обработал
        category = Category(
            name=name,
            slug=slug,
            parent_id=parent_id,
            type=category_type,
            is_active=is_active,
        )
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        logger.info("Category created with id %s", category.id)
        return category

    async def update_category(
        self,
        category_id: int,
        name: str,
        category_type: CategoryType,
        slug: str,
        parent_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Category]:
        """
        Обновить категорию по идентификатору.
        """
        logger.info("Updating category with id %s", category_id)
        category = await self.get_category_by_id(category_id, include_inactive=True)
        if category is None:
            logger.warning("Category with id %s not found for update", category_id)
            return None

        category.name = name
        category.slug = slug
        category.type = category_type
        category.parent_id = parent_id
        if is_active is not None:
            category.is_active = is_active

        await self.session.commit()
        await self.session.refresh(category)

        logger.info("Category with id %s successfully updated", category_id)
        return category

    async def deactivate_category(self, category_id: int) -> bool:
        logger.info("Deactivating category with id %s", category_id)
        category = await self.get_category_by_id(category_id, include_inactive=True)
        if category is None:
            logger.warning("Category with id %s not found for deactivation", category_id)
            return False

        self._mark_inactive_recursive(category)
        await self.session.commit()
        logger.info("Category with id %s successfully deactivated", category_id)
        return True

    def _mark_inactive_recursive(self, category: Category) -> None:
        category.is_active = False
        for child in category.children:
            self._mark_inactive_recursive(child)


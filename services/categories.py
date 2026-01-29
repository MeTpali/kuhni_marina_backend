import logging
from typing import List

from fastapi import HTTPException, status

from core.models.categories import CategoryType
from core.schemas.categories import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
    CategoryTreeNode,
    CategoryListResponse,
    CategoryDeleteResponse,
)
from repositories.categories import CategoryRepository

logger = logging.getLogger(__name__)


class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    async def get_all_categories(self) -> CategoryListResponse:
        logger.info("Service call: get_all_categories")
        categories = await self.repository.get_all_categories()
        tree = self._build_tree(categories)
        response = CategoryListResponse(
            items=tree,
            message="Список категорий успешно получен",
        )
        logger.info("Service: fetched %d root categories", len(tree))
        return response

    async def get_categories_by_type(self, category_type: CategoryType) -> CategoryListResponse:
        logger.info("Service call: get_categories_by_type %s", category_type)
        categories = await self.repository.get_categories_by_type(category_type)
        tree = self._build_tree(categories)
        response = CategoryListResponse(
            items=tree,
            message=f"Категории типа {category_type.value} успешно получены",
        )
        logger.info("Service: fetched %d root categories for type %s", len(tree), category_type)
        return response

    async def get_category_by_id(self, category_id: int) -> CategoryResponse:
        logger.info("Service call: get_category_by_id %s", category_id)
        category = await self.repository.get_category_by_id(category_id)
        if not category:
            logger.error("Category %s not found", category_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория с id {category_id} не найдена",
            )
        response = CategoryResponse(
            id=category.id,
            name=category.name,
            slug=category.slug,
            parent_id=category.parent_id,
            type=category.type,
            is_active=category.is_active,
            message="Категория успешно найдена",
        )
        logger.info("Service: category %s retrieved", category_id)
        return response

    async def create_category(self, request: CategoryCreateRequest) -> CategoryResponse:
        logger.info("Service call: create_category name=%s, slug=%s", request.name, request.slug)

        # Генерируем slug, если он не передан
        if request.slug is None or not request.slug.strip():
            logger.info("Generating slug from name '%s'", request.name)
            slug = await self.repository.generate_unique_slug(request.name)
        else:
            # Проверяем уникальность переданного slug
            slug = await self.repository.generate_unique_slug(request.slug)
            if slug != request.slug:
                logger.warning("Slug '%s' already exists, generated unique slug '%s'", request.slug, slug)

        if request.parent_id is not None:
            parent = await self.repository.get_category_by_id(request.parent_id)
            if not parent:
                logger.error("Parent category %s not found", request.parent_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Родительская категория с id {request.parent_id} не найдена",
                )

        category = await self.repository.create_category(
            name=request.name,
            slug=slug,
            category_type=request.type,
            parent_id=request.parent_id,
            is_active=request.is_active,
        )
        response = CategoryResponse(
            id=category.id,
            name=category.name,
            slug=category.slug,
            parent_id=category.parent_id,
            type=category.type,
            is_active=category.is_active,
            message="Категория успешно создана",
        )
        logger.info("Service: category %s created with slug '%s'", category.id, category.slug)
        return response

    async def update_category(
        self,
        category_id: int,
        request: CategoryUpdateRequest,
    ) -> CategoryResponse:
        """
        Обновить категорию по идентификатору.
        Если изменяется название, перегенерирует slug.
        """
        logger.info("Service call: update_category id=%s, name=%s", category_id, request.name)

        # Получаем текущую категорию (включая неактивные)
        current_category = await self.repository.get_category_by_id(category_id, include_inactive=True)
        if not current_category:
            logger.error("Category %s not found for update", category_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория с id {category_id} не найдена",
            )

        # Определяем, нужно ли перегенерировать slug
        name_changed = current_category.name != request.name
        
        if name_changed:
            # Если изменилось название, перегенерируем slug из нового названия
            logger.info("Category name changed from '%s' to '%s', regenerating slug", current_category.name, request.name)
            slug = await self.repository.generate_unique_slug(request.name, exclude_id=category_id)
        elif request.slug is not None and request.slug.strip():
            # Если slug передан явно, используем его (проверяем уникальность)
            slug = await self.repository.generate_unique_slug(request.slug, exclude_id=category_id)
            if slug != request.slug:
                logger.warning("Slug '%s' already exists, generated unique slug '%s'", request.slug, slug)
        else:
            # Если slug не передан и название не изменилось, оставляем текущий slug
            slug = current_category.slug

        # Проверяем родительскую категорию, если она указана
        if request.parent_id is not None:
            if request.parent_id == category_id:
                logger.error("Category cannot be its own parent")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Категория не может быть родителем самой себя",
                )
            parent = await self.repository.get_category_by_id(request.parent_id, include_inactive=True)
            if not parent:
                logger.error("Parent category %s not found", request.parent_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Родительская категория с id {request.parent_id} не найдена",
                )

        category = await self.repository.update_category(
            category_id=category_id,
            name=request.name,
            slug=slug,
            category_type=request.type,
            parent_id=request.parent_id,
            is_active=request.is_active if request.is_active is not None else current_category.is_active,
        )

        response = CategoryResponse(
            id=category.id,
            name=category.name,
            slug=category.slug,
            parent_id=category.parent_id,
            type=category.type,
            is_active=category.is_active,
            message="Категория успешно обновлена",
        )
        logger.info("Service: category %s updated with slug '%s'", category.id, category.slug)
        return response

    async def delete_category(self, category_id: int) -> CategoryDeleteResponse:
        logger.info("Service call: delete_category %s", category_id)
        success = await self.repository.deactivate_category(category_id)
        if not success:
            logger.error("Category %s not found for deletion", category_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория с id {category_id} не найдена",
            )
        response = CategoryDeleteResponse(
            category_id=category_id,
            message="Категория деактивирована",
        )
        logger.info("Service: category %s deactivated", category_id)
        return response

    def _build_tree(self, categories: List) -> List[CategoryTreeNode]:
        logger.debug("Building category tree from %d categories", len(categories))
        nodes: dict[int, CategoryTreeNode] = {}
        roots: List[CategoryTreeNode] = []

        for category in categories:
            node = CategoryTreeNode(
                id=category.id,
                name=category.name,
                slug=category.slug,
                parent_id=category.parent_id,
                type=category.type,
                is_active=category.is_active,
                message=None,
                children=[],
            )
            nodes[category.id] = node

        for category in categories:
            node = nodes[category.id]
            parent_id = category.parent_id
            if parent_id and parent_id in nodes:
                nodes[parent_id].children.append(node)
            else:
                roots.append(node)

        logger.debug("Built tree with %d root categories", len(roots))
        return roots


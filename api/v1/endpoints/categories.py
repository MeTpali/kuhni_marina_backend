from fastapi import APIRouter, Depends, status

from api.deps import get_category_service
from core.models.categories import CategoryType
from core.schemas.categories import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
    CategoryListResponse,
    CategoryDeleteResponse,
)
from services.categories import CategoryService

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={404: {"description": "Category not found"}},
)


@router.get(
    "",
    response_model=CategoryListResponse,
    summary="Получить все категории",
    description="Возвращает древовидный список всех активных категорий",
)
async def get_categories(
    category_service: CategoryService = Depends(get_category_service),
):
    """
    Получить все активные категории в виде дерева.
    """
    return await category_service.get_all_categories()


@router.get(
    "/type/{category_type}",
    response_model=CategoryListResponse,
    summary="Получить категории по типу",
    description="Возвращает древовидный список активных категорий указанного типа",
)
async def get_categories_by_type(
    category_type: CategoryType,
    category_service: CategoryService = Depends(get_category_service),
):
    """
    Получить активные категории по типу в виде дерева.
    """
    return await category_service.get_categories_by_type(category_type)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Получить категорию по идентификатору",
    description="Возвращает активную категорию по идентификатору",
    responses={
        200: {"description": "Категория найдена"},
        404: {"description": "Категория не найдена"},
    },
)
async def get_category_by_id(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
):
    """
    Получить активную категорию по идентификатору.
    """
    return await category_service.get_category_by_id(category_id)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать категорию",
    description="Создает новую категорию",
    responses={
        201: {"description": "Категория создана"},
        400: {"description": "Некорректные данные"},
        404: {"description": "Родительская категория не найдена"},
    },
)
async def create_category(
    request: CategoryCreateRequest,
    category_service: CategoryService = Depends(get_category_service),
):
    """
    Создать новую категорию.
    """
    return await category_service.create_category(request)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Обновить категорию",
    description="Обновляет категорию по идентификатору. Если изменяется название, автоматически перегенерирует slug",
    responses={
        200: {"description": "Категория успешно обновлена"},
        400: {"description": "Некорректные данные"},
        404: {"description": "Категория или родительская категория не найдена"},
    },
)
async def update_category(
    category_id: int,
    request: CategoryUpdateRequest,
    category_service: CategoryService = Depends(get_category_service),
):
    """
    Обновить категорию:
    - Если изменяется название, автоматически перегенерирует slug
    - Проверяет корректность данных и существование родительской категории
    - Обновляет и возвращает обновленную категорию
    """
    return await category_service.update_category(category_id, request)


@router.delete(
    "/{category_id}",
    response_model=CategoryDeleteResponse,
    summary="Деактивировать категорию",
    description="Помечает категорию и её дочерние категории как неактивные",
    responses={
        200: {"description": "Категория деактивирована"},
        404: {"description": "Категория не найдена"},
    },
)
async def delete_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
):
    """
    Деактивировать категорию и её дочерние категории.
    """
    return await category_service.delete_category(category_id)


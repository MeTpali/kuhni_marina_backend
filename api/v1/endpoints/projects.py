from fastapi import APIRouter, Depends, status

from api.deps import get_project_service
from services.projects import ProjectService
from core.schemas.projects import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectDeleteResponse,
)

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Project not found"}},
)


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="Получить все проекты",
    description="Возвращает список всех проектов",
)
async def get_projects(
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Получить список всех проектов:
    - Возвращает все существующие проекты
    - Отсортированы по дате создания (новые сначала)
    """
    return await project_service.get_all_projects()


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Получить проект по идентификатору",
    description="Возвращает проект с указанным идентификатором, включая изображения и список товаров",
    responses={
        200: {"description": "Проект найден"},
        404: {"description": "Проект не найден"},
    },
)
async def get_project_by_id(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Получить проект по идентификатору:
    - Возвращает проект с полной информацией
    - Включает список изображений проекта
    - Включает список идентификаторов товаров, использованных в проекте
    """
    return await project_service.get_project_by_id(project_id)


@router.get(
    "/product/{product_id}",
    response_model=ProjectListResponse,
    summary="Получить проекты по идентификатору продукта",
    description="Возвращает список проектов, в которых используется указанный продукт",
    responses={
        200: {"description": "Проекты найдены"},
    },
)
async def get_projects_by_product_id(
    product_id: int,
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Получить проекты по идентификатору продукта:
    - Возвращает все проекты, в которых используется указанный продукт
    - Отсортированы по дате создания (новые сначала)
    """
    return await project_service.get_projects_by_product_id(product_id)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать проект",
    description="Создает и возвращает новый проект",
    responses={
        201: {"description": "Проект успешно создан"},
        400: {"description": "Некорректные данные для проекта"},
    },
)
async def create_project(
    request: ProjectCreateRequest,
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Создать новый проект:
    - Проверяет корректность данных
    - Создает и возвращает созданный проект
    """
    return await project_service.create_project(request)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Обновить проект",
    description="Обновляет проект по идентификатору",
    responses={
        200: {"description": "Проект успешно обновлен"},
        400: {"description": "Некорректные данные для проекта"},
        404: {"description": "Проект не найден"},
    },
)
async def update_project(
    project_id: int,
    request: ProjectUpdateRequest,
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Обновить проект:
    - Проверяет корректность данных
    - Обновляет указанные поля проекта
    - Поля, которые не указаны, остаются без изменений
    """
    return await project_service.update_project(project_id, request)


@router.delete(
    "/{project_id}",
    response_model=ProjectDeleteResponse,
    summary="Удалить проект",
    description="Удаляет проект по идентификатору",
    responses={
        200: {"description": "Проект успешно удален"},
        404: {"description": "Проект не найден"},
    },
)
async def delete_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Удалить проект:
    - Удаляет проект по идентификатору
    - Каскадное удаление связанных сущностей (изображений и связей с продуктами) настроено в БД
    """
    return await project_service.delete_project(project_id)


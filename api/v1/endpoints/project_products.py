from fastapi import APIRouter, Depends, status

from api.deps import get_project_product_service
from services.project_products import ProjectProductService
from core.schemas.project_products import (
    ProjectProductCreateRequest,
    ProjectProductResponse,
    ProjectProductListResponse,
    ProjectProductDeleteResponse,
    ProjectIdsByProductResponse,
)

router = APIRouter(
    prefix="/project-products",
    tags=["project-products"],
    responses={404: {"description": "Project product not found"}},
)


@router.get(
    "",
    response_model=ProjectProductListResponse,
    summary="Получить все связи проектов с продуктами",
    description="Возвращает список всех связей проектов с продуктами",
)
async def get_project_products(
    project_product_service: ProjectProductService = Depends(get_project_product_service),
):
    """
    Получить список всех связей проектов с продуктами:
    - Возвращает все существующие связи
    - Отсортированы по project_id и product_id
    """
    return await project_product_service.get_all_project_products()


@router.get(
    "/product/{product_id}/projects",
    response_model=ProjectIdsByProductResponse,
    summary="Получить список идентификаторов проектов по идентификатору продукта",
    description="Возвращает список идентификаторов проектов, в которых используется указанный продукт",
    responses={
        200: {"description": "Список идентификаторов проектов успешно получен"},
    },
)
async def get_project_ids_by_product_id(
    product_id: int,
    project_product_service: ProjectProductService = Depends(get_project_product_service),
):
    """
    Получить список идентификаторов проектов по идентификатору продукта:
    - Возвращает список project_id для указанного product_id
    """
    return await project_product_service.get_project_ids_by_product_id(product_id)


@router.post(
    "",
    response_model=ProjectProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать связь проекта с продуктом",
    description="Создает и возвращает новую связь проекта с продуктом",
    responses={
        201: {"description": "Связь проекта с продуктом успешно создана"},
        400: {"description": "Некорректные данные или связь уже существует"},
    },
)
async def create_project_product(
    request: ProjectProductCreateRequest,
    project_product_service: ProjectProductService = Depends(get_project_product_service),
):
    """
    Создать новую связь проекта с продуктом:
    - Проверяет, что связь еще не существует
    - Создает и возвращает созданную связь
    """
    return await project_product_service.create_project_product(request)


@router.delete(
    "/{project_id}/{product_id}",
    response_model=ProjectProductDeleteResponse,
    summary="Удалить связь проекта с продуктом",
    description="Удаляет связь проекта с продуктом по идентификаторам",
    responses={
        200: {"description": "Связь проекта с продуктом успешно удалена"},
        404: {"description": "Связь проекта с продуктом не найдена"},
    },
)
async def delete_project_product(
    project_id: int,
    product_id: int,
    project_product_service: ProjectProductService = Depends(get_project_product_service),
):
    """
    Удалить связь проекта с продуктом:
    - Удаляет связь по идентификаторам проекта и продукта
    - Каскадное удаление связанных сущностей настроено в БД
    """
    return await project_product_service.delete_project_product(project_id, product_id)


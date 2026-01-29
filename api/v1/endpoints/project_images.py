from fastapi import APIRouter, Depends, status

from api.deps import get_project_image_service
from services.project_images import ProjectImageService
from core.schemas.project_images import (
    ProjectImageCreateRequest,
    ProjectImageCreateBulkRequest,
    ProjectImageResponse,
    ProjectImageListResponse,
    ProjectImageDeleteResponse,
)

router = APIRouter(
    prefix="/project-images",
    tags=["project-images"],
    responses={404: {"description": "Project image not found"}},
)


@router.get(
    "",
    response_model=ProjectImageListResponse,
    summary="Получить все изображения проектов",
    description="Возвращает список всех изображений проектов",
)
async def get_project_images(
    project_image_service: ProjectImageService = Depends(get_project_image_service),
):
    """
    Получить список всех изображений проектов:
    - Возвращает все существующие изображения проектов
    - Отсортированы по project_id и id
    """
    return await project_image_service.get_all_project_images()


@router.get(
    "/{project_image_id}",
    response_model=ProjectImageResponse,
    summary="Получить изображение проекта по идентификатору",
    description="Возвращает изображение проекта с указанным идентификатором",
    responses={
        200: {"description": "Изображение проекта найдено"},
        404: {"description": "Изображение проекта не найдено"},
    },
)
async def get_project_image_by_id(
    project_image_id: int,
    project_image_service: ProjectImageService = Depends(get_project_image_service),
):
    """
    Получить изображение проекта по идентификатору:
    - Возвращает изображение проекта, если оно существует
    - Возвращает ошибку 404, если изображение проекта не найдено
    """
    return await project_image_service.get_project_image_by_id(project_image_id)


@router.post(
    "",
    response_model=ProjectImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать изображение проекта",
    description="Создает и возвращает новое изображение проекта",
    responses={
        201: {"description": "Изображение проекта успешно создано"},
        400: {"description": "Некорректные данные для изображения проекта"},
    },
)
async def create_project_image(
    request: ProjectImageCreateRequest,
    project_image_service: ProjectImageService = Depends(get_project_image_service),
):
    """
    Создать новое изображение проекта:
    - Проверяет корректность данных
    - Создает и возвращает созданное изображение проекта
    """
    return await project_image_service.create_project_image(request)


@router.post(
    "/bulk",
    response_model=ProjectImageListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать несколько изображений проекта",
    description="Создает и возвращает несколько новых изображений проекта",
    responses={
        201: {"description": "Изображения проекта успешно созданы"},
        400: {"description": "Некорректные данные для изображений проекта"},
    },
)
async def create_multiple_project_images(
    request: ProjectImageCreateBulkRequest,
    project_image_service: ProjectImageService = Depends(get_project_image_service),
):
    """
    Создать несколько изображений проекта:
    - Проверяет корректность данных для всех изображений
    - Создает и возвращает список созданных изображений проекта
    """
    return await project_image_service.create_multiple_project_images(request)


@router.delete(
    "/{project_image_id}",
    response_model=ProjectImageDeleteResponse,
    summary="Удалить изображение проекта",
    description="Удаляет изображение проекта по идентификатору",
    responses={
        200: {"description": "Изображение проекта успешно удалено"},
        404: {"description": "Изображение проекта не найдено"},
    },
)
async def delete_project_image(
    project_image_id: int,
    project_image_service: ProjectImageService = Depends(get_project_image_service),
):
    """
    Удалить изображение проекта:
    - Удаляет изображение проекта по идентификатору
    - Каскадное удаление связанных сущностей настроено в БД
    """
    return await project_image_service.delete_project_image(project_image_id)


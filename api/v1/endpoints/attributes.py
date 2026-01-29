from fastapi import APIRouter, Depends, status

from api.deps import get_attribute_service
from services.attributes import AttributeService
from core.schemas.attributes import (
    AttributeCreateRequest,
    AttributeUpdateRequest,
    AttributeResponse,
    AttributeListResponse,
    AttributeDeleteResponse,
)

router = APIRouter(
    prefix="/attributes",
    tags=["attributes"],
    responses={404: {"description": "Attribute not found"}},
)


@router.get(
    "",
    response_model=AttributeListResponse,
    summary="Получить все атрибуты",
    description="Возвращает список всех атрибутов",
)
async def get_attributes(
    attribute_service: AttributeService = Depends(get_attribute_service),
):
    """
    Получить список всех атрибутов:
    - Возвращает все существующие атрибуты
    """
    return await attribute_service.get_all_attributes()


@router.get(
    "/{attribute_id}",
    response_model=AttributeResponse,
    summary="Получить атрибут по идентификатору",
    description="Возвращает атрибут с указанным идентификатором",
    responses={
        200: {"description": "Атрибут найден"},
        404: {"description": "Атрибут не найден"},
    },
)
async def get_attribute_by_id(
    attribute_id: int,
    attribute_service: AttributeService = Depends(get_attribute_service),
):
    """
    Получить атрибут по идентификатору:
    - Возвращает атрибут, если он существует
    - Возвращает ошибку 404, если атрибут не найден
    """
    return await attribute_service.get_attribute_by_id(attribute_id)


@router.post(
    "",
    response_model=AttributeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать атрибут",
    description="Создает и возвращает новый атрибут",
    responses={
        201: {"description": "Атрибут успешно создан"},
        400: {"description": "Некорректные данные для атрибута"},
    },
)
async def create_attribute(
    request: AttributeCreateRequest,
    attribute_service: AttributeService = Depends(get_attribute_service),
):
    """
    Создать новый атрибут:
    - Проверяет корректность данных
    - Создает и возвращает созданный атрибут
    """
    return await attribute_service.create_attribute(request)


@router.put(
    "/{attribute_id}",
    response_model=AttributeResponse,
    summary="Обновить атрибут",
    description="Обновляет атрибут по идентификатору",
    responses={
        200: {"description": "Атрибут успешно обновлен"},
        400: {"description": "Некорректные данные для атрибута"},
        404: {"description": "Атрибут не найден"},
    },
)
async def update_attribute(
    attribute_id: int,
    request: AttributeUpdateRequest,
    attribute_service: AttributeService = Depends(get_attribute_service),
):
    """
    Обновить атрибут:
    - Проверяет корректность данных
    - Обновляет и возвращает обновленный атрибут
    """
    return await attribute_service.update_attribute(attribute_id, request)


@router.delete(
    "/{attribute_id}",
    response_model=AttributeDeleteResponse,
    summary="Удалить атрибут",
    description="Удаляет атрибут по идентификатору",
    responses={
        200: {"description": "Атрибут успешно удален"},
        404: {"description": "Атрибут не найден"},
    },
)
async def delete_attribute(
    attribute_id: int,
    attribute_service: AttributeService = Depends(get_attribute_service),
):
    """
    Удалить атрибут:
    - Удаляет атрибут по идентификатору
    - Каскадное удаление связанных сущностей настроено в БД
    """
    return await attribute_service.delete_attribute(attribute_id)


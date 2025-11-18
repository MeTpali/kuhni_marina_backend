from fastapi import APIRouter, Depends, Query, status
from typing import Optional

from api.deps import get_measure_request_service
from services.measure_requests import MeasureRequestService
from core.models.measure_requests import MeasureRequestStatus
from core.schemas.measure_requests import (
    MeasureRequestCreateRequest,
    MeasureRequestUpdateRequest,
    MeasureRequestStatusUpdateRequest,
    MeasureRequestResponse,
    MeasureRequestListResponse,
)

router = APIRouter(
    prefix="/measure-requests",
    tags=["measure-requests"],
    responses={404: {"description": "Measure request not found"}},
)


@router.get(
    "",
    response_model=MeasureRequestListResponse,
    summary="Получить все замеры",
    description="Возвращает список всех замеров с возможностью фильтрации по статусу",
)
async def get_measure_requests(
    status: Optional[MeasureRequestStatus] = Query(None, description="Фильтр по статусу"),
    measure_request_service: MeasureRequestService = Depends(get_measure_request_service),
):
    """
    Получить список всех замеров:
    - Возвращает все существующие замеры
    - Опциональная фильтрация по статусу через query параметр
    - Отсортированы по дате создания (новые сначала)
    """
    return await measure_request_service.get_all_measure_requests(status)


@router.get(
    "/{measure_request_id}",
    response_model=MeasureRequestResponse,
    summary="Получить замер по идентификатору",
    description="Возвращает замер с указанным идентификатором",
    responses={
        200: {"description": "Замер найден"},
        404: {"description": "Замер не найден"},
    },
)
async def get_measure_request_by_id(
    measure_request_id: int,
    measure_request_service: MeasureRequestService = Depends(get_measure_request_service),
):
    """
    Получить замер по идентификатору:
    - Возвращает замер, если он существует
    - Возвращает ошибку 404, если замер не найден
    """
    return await measure_request_service.get_measure_request_by_id(measure_request_id)


@router.post(
    "",
    response_model=MeasureRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать замер",
    description="Создает и возвращает новый замер",
    responses={
        201: {"description": "Замер успешно создан"},
        400: {"description": "Некорректные данные для замера"},
    },
)
async def create_measure_request(
    request: MeasureRequestCreateRequest,
    measure_request_service: MeasureRequestService = Depends(get_measure_request_service),
):
    """
    Создать новый замер:
    - Проверяет корректность данных
    - Создает и возвращает созданный замер
    - По умолчанию статус устанавливается в NEW
    """
    return await measure_request_service.create_measure_request(request)


@router.put(
    "/{measure_request_id}",
    response_model=MeasureRequestResponse,
    summary="Обновить замер",
    description="Обновляет замер по идентификатору",
    responses={
        200: {"description": "Замер успешно обновлен"},
        400: {"description": "Некорректные данные для замера"},
        404: {"description": "Замер не найден"},
    },
)
async def update_measure_request(
    measure_request_id: int,
    request: MeasureRequestUpdateRequest,
    measure_request_service: MeasureRequestService = Depends(get_measure_request_service),
):
    """
    Обновить замер:
    - Обновляет указанные поля замера
    - Поля, которые не указаны, остаются без изменений
    """
    return await measure_request_service.update_measure_request(measure_request_id, request)


@router.patch(
    "/{measure_request_id}/status",
    response_model=MeasureRequestResponse,
    summary="Обновить статус замера",
    description="Обновляет статус замера по идентификатору",
    responses={
        200: {"description": "Статус замера успешно обновлен"},
        404: {"description": "Замер не найден"},
    },
)
async def update_measure_request_status(
    measure_request_id: int,
    request: MeasureRequestStatusUpdateRequest,
    measure_request_service: MeasureRequestService = Depends(get_measure_request_service),
):
    """
    Обновить статус замера:
    - Обновляет только статус замера
    - Доступные статусы: NEW, IN_PROGRESS, DONE, CANCELLED
    """
    return await measure_request_service.update_measure_request_status(measure_request_id, request)


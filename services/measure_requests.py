import logging

from fastapi import HTTPException, status

from repositories.measure_requests import MeasureRequestRepository
from core.models.measure_requests import MeasureRequestStatus
from core.schemas.measure_requests import (
    MeasureRequestCreateRequest,
    MeasureRequestUpdateRequest,
    MeasureRequestStatusUpdateRequest,
    MeasureRequestResponse,
    MeasureRequestListResponse,
)

logger = logging.getLogger(__name__)


class MeasureRequestService:
    def __init__(self, repository: MeasureRequestRepository):
        self.repository = repository

    async def get_all_measure_requests(
        self, status_filter: MeasureRequestStatus | None = None
    ) -> MeasureRequestListResponse:
        """
        Получить список всех замеров с опциональной фильтрацией по статусу.
        """
        logger.info("Fetching all measure requests via service with status filter: %s", status_filter)
        measure_requests = await self.repository.get_all_measure_requests(status_filter)
        items = [
            MeasureRequestResponse(
                id=mr.id,
                full_name=mr.full_name,
                phone=mr.phone,
                address=mr.address,
                preferred_date=mr.preferred_date,
                comment=mr.comment,
                status=mr.status,
                created_at=mr.created_at,
                message=None,
            )
            for mr in measure_requests
        ]

        response = MeasureRequestListResponse(
            items=items,
            message="Список замеров успешно получен",
        )
        logger.info("Successfully fetched %d measure requests", len(items))
        return response

    async def get_measure_request_by_id(
        self, measure_request_id: int
    ) -> MeasureRequestResponse:
        """
        Получить замер по идентификатору.
        """
        logger.info("Fetching measure request by id: %s via service", measure_request_id)
        measure_request = await self.repository.get_measure_request_by_id(measure_request_id)
        if not measure_request:
            logger.error("Measure request with id %s not found", measure_request_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Замер с id {measure_request_id} не найден",
            )

        response = MeasureRequestResponse(
            id=measure_request.id,
            full_name=measure_request.full_name,
            phone=measure_request.phone,
            address=measure_request.address,
            preferred_date=measure_request.preferred_date,
            comment=measure_request.comment,
            status=measure_request.status,
            created_at=measure_request.created_at,
            message="Замер успешно найден",
        )
        logger.info("Measure request with id %s successfully retrieved", measure_request_id)
        return response

    async def create_measure_request(
        self,
        request: MeasureRequestCreateRequest,
    ) -> MeasureRequestResponse:
        """
        Создать новый замер.
        """
        logger.info("Creating measure request via service for '%s'", request.full_name)

        if len(request.full_name.strip()) < 2:
            logger.error("Measure request full_name too short: '%s'", request.full_name)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя клиента должно содержать минимум 2 символа",
            )

        if len(request.phone.strip()) < 5:
            logger.error("Measure request phone too short: '%s'", request.phone)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Телефон должен содержать минимум 5 символов",
            )

        if len(request.address.strip()) < 5:
            logger.error("Measure request address too short: '%s'", request.address)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Адрес должен содержать минимум 5 символов",
            )

        measure_request = await self.repository.create_measure_request(request)

        response = MeasureRequestResponse(
            id=measure_request.id,
            full_name=measure_request.full_name,
            phone=measure_request.phone,
            address=measure_request.address,
            preferred_date=measure_request.preferred_date,
            comment=measure_request.comment,
            status=measure_request.status,
            created_at=measure_request.created_at,
            message="Замер успешно создан",
        )
        logger.info("Measure request created with id %s via service", measure_request.id)
        return response

    async def update_measure_request(
        self,
        measure_request_id: int,
        request: MeasureRequestUpdateRequest,
    ) -> MeasureRequestResponse:
        """
        Обновить замер.
        """
        logger.info("Updating measure request via service with id %s", measure_request_id)

        if request.full_name is not None and len(request.full_name.strip()) < 2:
            logger.error("Measure request full_name too short: '%s'", request.full_name)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя клиента должно содержать минимум 2 символа",
            )

        if request.phone is not None and len(request.phone.strip()) < 5:
            logger.error("Measure request phone too short: '%s'", request.phone)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Телефон должен содержать минимум 5 символов",
            )

        if request.address is not None and len(request.address.strip()) < 5:
            logger.error("Measure request address too short: '%s'", request.address)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Адрес должен содержать минимум 5 символов",
            )

        measure_request = await self.repository.update_measure_request(measure_request_id, request)
        if not measure_request:
            logger.error("Measure request with id %s not found for update", measure_request_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Замер с id {measure_request_id} не найден",
            )

        response = MeasureRequestResponse(
            id=measure_request.id,
            full_name=measure_request.full_name,
            phone=measure_request.phone,
            address=measure_request.address,
            preferred_date=measure_request.preferred_date,
            comment=measure_request.comment,
            status=measure_request.status,
            created_at=measure_request.created_at,
            message="Замер успешно обновлен",
        )
        logger.info("Measure request with id %s successfully updated via service", measure_request_id)
        return response

    async def update_measure_request_status(
        self,
        measure_request_id: int,
        request: MeasureRequestStatusUpdateRequest,
    ) -> MeasureRequestResponse:
        """
        Обновить статус замера.
        """
        logger.info("Updating measure request status via service with id %s to %s", measure_request_id, request.status)
        measure_request = await self.repository.update_measure_request_status(measure_request_id, request.status)
        if not measure_request:
            logger.error("Measure request with id %s not found for status update", measure_request_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Замер с id {measure_request_id} не найден",
            )

        response = MeasureRequestResponse(
            id=measure_request.id,
            full_name=measure_request.full_name,
            phone=measure_request.phone,
            address=measure_request.address,
            preferred_date=measure_request.preferred_date,
            comment=measure_request.comment,
            status=measure_request.status,
            created_at=measure_request.created_at,
            message="Статус замера успешно обновлен",
        )
        logger.info("Measure request status with id %s successfully updated via service", measure_request_id)
        return response


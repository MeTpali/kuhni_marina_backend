from typing import List, Optional
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.measure_requests import MeasureRequest, MeasureRequestStatus
from core.schemas.measure_requests import (
    MeasureRequestCreateRequest,
    MeasureRequestUpdateRequest,
)

logger = logging.getLogger(__name__)


class MeasureRequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_measure_requests(
        self, status: Optional[MeasureRequestStatus] = None
    ) -> List[MeasureRequest]:
        """
        Получить список всех замеров с опциональной фильтрацией по статусу.
        """
        logger.info("Fetching all measure requests with status filter: %s", status)
        query = select(MeasureRequest)
        
        if status is not None:
            query = query.where(MeasureRequest.status == status)
        
        query = query.order_by(MeasureRequest.created_at.desc(), MeasureRequest.id)
        result = await self.session.execute(query)
        measure_requests = result.scalars().all()
        logger.info("Retrieved %d measure requests", len(measure_requests))
        return measure_requests

    async def get_measure_request_by_id(
        self, measure_request_id: int
    ) -> Optional[MeasureRequest]:
        """
        Получить замер по идентификатору.
        """
        logger.info("Fetching measure request with id %s", measure_request_id)
        query = select(MeasureRequest).where(MeasureRequest.id == measure_request_id)
        result = await self.session.execute(query)
        measure_request = result.scalar_one_or_none()

        if measure_request is None:
            logger.warning("Measure request with id %s not found", measure_request_id)
        return measure_request

    async def create_measure_request(
        self, request: MeasureRequestCreateRequest
    ) -> MeasureRequest:
        """
        Создать новый замер.
        """
        logger.info("Creating measure request for '%s'", request.full_name)
        measure_request = MeasureRequest(
            full_name=request.full_name,
            phone=request.phone,
            address=request.address,
            preferred_date=request.preferred_date,
            comment=request.comment,
            status=request.status if request.status is not None else MeasureRequestStatus.NEW,
        )

        self.session.add(measure_request)
        await self.session.commit()
        await self.session.refresh(measure_request)

        logger.info("Measure request created with id %s", measure_request.id)
        return measure_request

    async def update_measure_request(
        self, measure_request_id: int, request: MeasureRequestUpdateRequest
    ) -> Optional[MeasureRequest]:
        """
        Обновить замер.
        """
        logger.info("Updating measure request with id %s", measure_request_id)
        measure_request = await self.get_measure_request_by_id(measure_request_id)
        if measure_request is None:
            logger.warning("Measure request with id %s not found for update", measure_request_id)
            return None

        if request.full_name is not None:
            measure_request.full_name = request.full_name
        if request.phone is not None:
            measure_request.phone = request.phone
        if request.address is not None:
            measure_request.address = request.address
        if request.preferred_date is not None:
            measure_request.preferred_date = request.preferred_date
        if request.comment is not None:
            measure_request.comment = request.comment
        if request.status is not None:
            measure_request.status = request.status

        await self.session.commit()
        await self.session.refresh(measure_request)

        logger.info("Measure request with id %s successfully updated", measure_request_id)
        return measure_request

    async def update_measure_request_status(
        self, measure_request_id: int, status: MeasureRequestStatus
    ) -> Optional[MeasureRequest]:
        """
        Обновить статус замера.
        """
        logger.info("Updating measure request status with id %s to %s", measure_request_id, status)
        measure_request = await self.get_measure_request_by_id(measure_request_id)
        if measure_request is None:
            logger.warning("Measure request with id %s not found for status update", measure_request_id)
            return None

        measure_request.status = status
        await self.session.commit()
        await self.session.refresh(measure_request)

        logger.info("Measure request status with id %s successfully updated to %s", measure_request_id, status)
        return measure_request


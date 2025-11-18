import logging

from fastapi import HTTPException, status

from repositories.attributes import AttributeRepository
from core.schemas.attributes import (
    AttributeCreateRequest,
    AttributeResponse,
    AttributeListResponse,
    AttributeDeleteResponse,
)

logger = logging.getLogger(__name__)


class AttributeService:
    def __init__(self, repository: AttributeRepository):
        self.repository = repository

    async def get_all_attributes(self) -> AttributeListResponse:
        """
        Получить список всех атрибутов.
        """
        logger.info("Fetching all attributes via service")
        attributes = await self.repository.get_all_attributes()
        items = [
            AttributeResponse(
                id=attribute.id,
                name=attribute.name,
                unit=attribute.unit,
                message=None,
            )
            for attribute in attributes
        ]

        response = AttributeListResponse(
            items=items,
            message="Список атрибутов успешно получен",
        )
        logger.info("Successfully fetched %d attributes", len(items))
        return response

    async def get_attribute_by_id(self, attribute_id: int) -> AttributeResponse:
        """
        Получить атрибут по идентификатору.
        """
        logger.info("Fetching attribute by id: %s via service", attribute_id)
        attribute = await self.repository.get_attribute_by_id(attribute_id)
        if not attribute:
            logger.error("Attribute with id %s not found", attribute_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Атрибут с id {attribute_id} не найден",
            )

        response = AttributeResponse(
            id=attribute.id,
            name=attribute.name,
            unit=attribute.unit,
            message="Атрибут успешно найден",
        )
        logger.info("Attribute with id %s successfully retrieved", attribute_id)
        return response

    async def create_attribute(
        self,
        request: AttributeCreateRequest,
    ) -> AttributeResponse:
        """
        Создать новый атрибут.
        """
        logger.info("Creating attribute via service with name '%s'", request.name)

        if len(request.name.strip()) < 2:
            logger.error("Attribute name too short: '%s'", request.name)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Название атрибута должно содержать минимум 2 символа",
            )

        attribute = await self.repository.create_attribute(request)

        response = AttributeResponse(
            id=attribute.id,
            name=attribute.name,
            unit=attribute.unit,
            message="Атрибут успешно создан",
        )
        logger.info("Attribute created with id %s via service", attribute.id)
        return response

    async def delete_attribute(self, attribute_id: int) -> AttributeDeleteResponse:
        """
        Удалить атрибут по идентификатору.
        """
        logger.info("Deleting attribute via service with id %s", attribute_id)
        success = await self.repository.delete_attribute(attribute_id)
        if not success:
            logger.error("Attribute with id %s not found for deletion", attribute_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Атрибут с id {attribute_id} не найден",
            )

        response = AttributeDeleteResponse(
            attribute_id=attribute_id,
            message="Атрибут успешно удален",
        )
        logger.info("Attribute with id %s successfully deleted via service", attribute_id)
        return response


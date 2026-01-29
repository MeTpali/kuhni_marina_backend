from typing import List, Optional
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.attributes import Attribute
from core.schemas.attributes import AttributeCreateRequest, AttributeUpdateRequest

logger = logging.getLogger(__name__)


class AttributeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_attributes(self) -> List[Attribute]:
        """
        Получить список всех атрибутов.
        """
        logger.info("Fetching all attributes")
        query = select(Attribute).order_by(Attribute.id)
        result = await self.session.execute(query)
        attributes = result.scalars().all()
        logger.info("Retrieved %d attributes", len(attributes))
        return attributes

    async def get_attribute_by_id(self, attribute_id: int) -> Optional[Attribute]:
        """
        Получить атрибут по идентификатору.
        """
        logger.info("Fetching attribute with id %s", attribute_id)
        query = select(Attribute).where(Attribute.id == attribute_id)
        result = await self.session.execute(query)
        attribute = result.scalar_one_or_none()

        if attribute is None:
            logger.warning("Attribute with id %s not found", attribute_id)
        return attribute

    async def create_attribute(self, request: AttributeCreateRequest) -> Attribute:
        """
        Создать новый атрибут.
        """
        logger.info("Creating attribute with name '%s'", request.name)
        attribute = Attribute(
            name=request.name,
            unit=request.unit,
        )

        self.session.add(attribute)
        await self.session.commit()
        await self.session.refresh(attribute)

        logger.info("Attribute created with id %s", attribute.id)
        return attribute

    async def update_attribute(
        self, attribute_id: int, request: AttributeUpdateRequest
    ) -> Optional[Attribute]:
        """
        Обновить атрибут по идентификатору.
        """
        logger.info("Updating attribute with id %s", attribute_id)
        attribute = await self.get_attribute_by_id(attribute_id)
        if attribute is None:
            logger.warning("Attribute with id %s not found for update", attribute_id)
            return None

        attribute.name = request.name
        attribute.unit = request.unit

        await self.session.commit()
        await self.session.refresh(attribute)

        logger.info("Attribute with id %s successfully updated", attribute_id)
        return attribute

    async def delete_attribute(self, attribute_id: int) -> bool:
        """
        Удалить атрибут по идентификатору.
        """
        logger.info("Deleting attribute with id %s", attribute_id)
        attribute = await self.get_attribute_by_id(attribute_id)
        if attribute is None:
            logger.warning("Attribute with id %s not found for deletion", attribute_id)
            return False

        await self.session.delete(attribute)
        await self.session.commit()

        logger.info("Attribute with id %s successfully deleted", attribute_id)
        return True


import logging
from typing import List, Optional
from math import ceil
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select

from repositories.discounts import DiscountRepository
from core.models.campaigns import Campaign
from core.models.discounts import DiscountType, DiscountScope
from core.models.products import ProductType
from core.schemas.discounts import (
    DiscountCreateRequest,
    DiscountUpdateRequest,
    DiscountCampaignInfo,
    DiscountResponse,
    DiscountListResponse,
    DiscountDeleteResponse,
)

logger = logging.getLogger(__name__)


class DiscountService:
    def __init__(self, repository: DiscountRepository):
        self.repository = repository

    async def get_discounts(
        self,
        page: int = 1,
        page_size: int = 20,
        include_inactive: bool = False,
        scope: Optional[DiscountScope] = None,
        discount_type: Optional[DiscountType] = None,
        campaign_id: Optional[int] = None,
        product_id: Optional[int] = None,
        category_id: Optional[int] = None,
        product_type: Optional[ProductType] = None,
        is_active: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> DiscountListResponse:
        """
        Получить список скидок с фильтрацией и сортировкой.
        """
        logger.info(
            "Service call: get_discounts page=%s, page_size=%s, scope=%s, discount_type=%s",
            page, page_size, scope, discount_type
        )

        discounts, total = await self.repository.get_discounts(
            page=page,
            page_size=page_size,
            include_inactive=include_inactive,
            scope=scope,
            discount_type=discount_type,
            campaign_id=campaign_id,
            product_id=product_id,
            category_id=category_id,
            product_type=product_type,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        items = [
            DiscountResponse(
                id=discount.id,
                name=discount.name,
                discount_type=discount.discount_type,
                value=discount.value,
                scope=discount.scope,
                campaign_id=discount.campaign_id,
                product_id=discount.product_id,
                category_id=discount.category_id,
                product_type=discount.product_type,
                start_date=discount.start_date,
                end_date=discount.end_date,
                is_active=discount.is_active,
                priority=discount.priority,
                created_at=discount.created_at,
                updated_at=discount.updated_at,
                campaign=DiscountCampaignInfo(
                    id=discount.campaign.id,
                    name=discount.campaign.name,
                    slug=discount.campaign.slug,
                    badge_text=discount.campaign.badge_text,
                    landing_url=discount.campaign.landing_url,
                ) if discount.campaign else None,
                message=None,
            )
            for discount in discounts
        ]

        total_pages = ceil(total / page_size) if page_size > 0 else 0

        response = DiscountListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            message="Список скидок успешно получен",
        )
        logger.info("Service: fetched %d discounts (total: %d)", len(items), total)
        return response

    async def get_discount_by_id(self, discount_id: int) -> DiscountResponse:
        """
        Получить скидку по идентификатору.
        """
        logger.info("Service call: get_discount_by_id %s", discount_id)
        discount = await self.repository.get_discount_by_id(discount_id)
        if not discount:
            logger.error("Discount %s not found", discount_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Скидка с id {discount_id} не найдена",
            )

        response = DiscountResponse(
            id=discount.id,
            name=discount.name,
            discount_type=discount.discount_type,
            value=discount.value,
            scope=discount.scope,
            campaign_id=discount.campaign_id,
            product_id=discount.product_id,
            category_id=discount.category_id,
            product_type=discount.product_type,
            start_date=discount.start_date,
            end_date=discount.end_date,
            is_active=discount.is_active,
            priority=discount.priority,
            created_at=discount.created_at,
            updated_at=discount.updated_at,
            campaign=DiscountCampaignInfo(
                id=discount.campaign.id,
                name=discount.campaign.name,
                slug=discount.campaign.slug,
                badge_text=discount.campaign.badge_text,
                landing_url=discount.campaign.landing_url,
            ) if discount.campaign else None,
            message="Скидка успешно найдена",
        )
        logger.info("Service: discount %s retrieved", discount_id)
        return response

    async def create_discount(self, request: DiscountCreateRequest) -> DiscountResponse:
        """
        Создать новую скидку.
        """
        logger.info("Service call: create_discount name=%s", request.name)

        # Валидация данных
        if request.start_date >= request.end_date:
            logger.error("Invalid date range: start_date >= end_date")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дата начала должна быть раньше даты окончания",
            )

        if request.value <= 0:
            logger.error("Invalid discount value: %s", request.value)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Значение скидки должно быть больше нуля",
            )

        if request.discount_type == DiscountType.PERCENTAGE and request.value > 100:
            logger.error("Invalid percentage: %s", request.value)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Процентная скидка не может быть больше 100%",
            )

        # Проверка соответствия scope и привязок
        if request.scope == DiscountScope.PRODUCT and request.product_id is None:
            logger.error("Product scope requires product_id")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для скидки на продукт необходимо указать product_id",
            )

        if request.scope == DiscountScope.CATEGORY and request.category_id is None:
            logger.error("Category scope requires category_id")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для скидки на категорию необходимо указать category_id",
            )

        if request.scope == DiscountScope.TYPE and request.product_type is None:
            logger.error("Type scope requires product_type")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для скидки на тип продукта необходимо указать product_type",
            )

        if request.campaign_id is not None:
            campaign_result = await self.repository.session.execute(
                select(Campaign.id).where(Campaign.id == request.campaign_id)
            )
            if campaign_result.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Акция с id {request.campaign_id} не найдена",
                )

        discount = await self.repository.create_discount(request)

        response = DiscountResponse(
            id=discount.id,
            name=discount.name,
            discount_type=discount.discount_type,
            value=discount.value,
            scope=discount.scope,
            campaign_id=discount.campaign_id,
            product_id=discount.product_id,
            category_id=discount.category_id,
            product_type=discount.product_type,
            start_date=discount.start_date,
            end_date=discount.end_date,
            is_active=discount.is_active,
            priority=discount.priority,
            created_at=discount.created_at,
            updated_at=discount.updated_at,
            campaign=DiscountCampaignInfo(
                id=discount.campaign.id,
                name=discount.campaign.name,
                slug=discount.campaign.slug,
                badge_text=discount.campaign.badge_text,
                landing_url=discount.campaign.landing_url,
            ) if discount.campaign else None,
            message="Скидка успешно создана",
        )
        logger.info("Service: discount %s created", discount.id)
        return response

    async def update_discount(
        self,
        discount_id: int,
        request: DiscountUpdateRequest,
    ) -> DiscountResponse:
        """
        Обновить скидку по идентификатору.
        """
        logger.info("Service call: update_discount id=%s", discount_id)

        discount = await self.repository.get_discount_by_id(discount_id, include_inactive=True)
        if not discount:
            logger.error("Discount %s not found for update", discount_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Скидка с id {discount_id} не найдена",
            )

        # Валидация данных
        start_date = request.start_date if request.start_date is not None else discount.start_date
        end_date = request.end_date if request.end_date is not None else discount.end_date

        if start_date >= end_date:
            logger.error("Invalid date range: start_date >= end_date")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дата начала должна быть раньше даты окончания",
            )

        value = request.value if request.value is not None else discount.value
        discount_type = request.discount_type if request.discount_type is not None else discount.discount_type

        if value is not None and value <= 0:
            logger.error("Invalid discount value: %s", value)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Значение скидки должно быть больше нуля",
            )

        if discount_type == DiscountType.PERCENTAGE and value is not None and value > 100:
            logger.error("Invalid percentage: %s", value)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Процентная скидка не может быть больше 100%",
            )

        # Проверка соответствия scope и привязок
        scope = request.scope if request.scope is not None else discount.scope
        product_id = request.product_id if request.product_id is not None else discount.product_id
        category_id = request.category_id if request.category_id is not None else discount.category_id
        product_type = request.product_type if request.product_type is not None else discount.product_type

        if scope == DiscountScope.PRODUCT and product_id is None:
            logger.error("Product scope requires product_id")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для скидки на продукт необходимо указать product_id",
            )

        if scope == DiscountScope.CATEGORY and category_id is None:
            logger.error("Category scope requires category_id")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для скидки на категорию необходимо указать category_id",
            )

        if scope == DiscountScope.TYPE and product_type is None:
            logger.error("Type scope requires product_type")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для скидки на тип продукта необходимо указать product_type",
            )

        if request.campaign_id is not None:
            campaign_result = await self.repository.session.execute(
                select(Campaign.id).where(Campaign.id == request.campaign_id)
            )
            if campaign_result.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Акция с id {request.campaign_id} не найдена",
                )

        updated_discount = await self.repository.update_discount(discount_id, request)
        if not updated_discount:
            logger.error("Failed to update discount %s", discount_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при обновлении скидки",
            )

        response = DiscountResponse(
            id=updated_discount.id,
            name=updated_discount.name,
            discount_type=updated_discount.discount_type,
            value=updated_discount.value,
            scope=updated_discount.scope,
            campaign_id=updated_discount.campaign_id,
            product_id=updated_discount.product_id,
            category_id=updated_discount.category_id,
            product_type=updated_discount.product_type,
            start_date=updated_discount.start_date,
            end_date=updated_discount.end_date,
            is_active=updated_discount.is_active,
            priority=updated_discount.priority,
            created_at=updated_discount.created_at,
            updated_at=updated_discount.updated_at,
            campaign=DiscountCampaignInfo(
                id=updated_discount.campaign.id,
                name=updated_discount.campaign.name,
                slug=updated_discount.campaign.slug,
                badge_text=updated_discount.campaign.badge_text,
                landing_url=updated_discount.campaign.landing_url,
            ) if updated_discount.campaign else None,
            message="Скидка успешно обновлена",
        )
        logger.info("Service: discount %s updated", discount_id)
        return response

    async def delete_discount(self, discount_id: int) -> DiscountDeleteResponse:
        """
        Удалить скидку по идентификатору (soft delete через is_active=False).
        """
        logger.info("Service call: delete_discount %s", discount_id)
        success = await self.repository.deactivate_discount(discount_id)
        if not success:
            logger.error("Discount %s not found for deletion", discount_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Скидка с id {discount_id} не найдена",
            )

        response = DiscountDeleteResponse(
            discount_id=discount_id,
            message="Скидка успешно удалена",
        )
        logger.info("Service: discount %s deactivated", discount_id)
        return response

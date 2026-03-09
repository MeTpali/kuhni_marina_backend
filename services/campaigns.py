import logging
from math import ceil

from fastapi import HTTPException, status

from repositories.campaigns import CampaignRepository
from core.schemas.campaigns import (
    CampaignCreateRequest,
    CampaignUpdateRequest,
    CampaignResponse,
    CampaignListResponse,
    CampaignDeleteResponse,
)

logger = logging.getLogger(__name__)


class CampaignService:
    def __init__(self, repository: CampaignRepository):
        self.repository = repository

    async def get_campaigns(
        self,
        page: int = 1,
        page_size: int = 20,
        include_inactive: bool = False,
    ) -> CampaignListResponse:
        campaigns, total = await self.repository.get_campaigns(
            page=page,
            page_size=page_size,
            include_inactive=include_inactive,
        )

        items = [
            CampaignResponse(
                id=campaign.id,
                name=campaign.name,
                slug=campaign.slug,
                description=campaign.description,
                banner_image_url=campaign.banner_image_url,
                landing_url=campaign.landing_url,
                badge_text=campaign.badge_text,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                is_active=campaign.is_active,
                priority=campaign.priority,
                created_at=campaign.created_at,
                updated_at=campaign.updated_at,
                message=None,
            )
            for campaign in campaigns
        ]

        return CampaignListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size) if page_size > 0 else 0,
            message="Список акций успешно получен",
        )

    async def get_campaign_by_id(self, campaign_id: int) -> CampaignResponse:
        campaign = await self.repository.get_campaign_by_id(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Акция с id {campaign_id} не найдена",
            )

        return CampaignResponse(
            id=campaign.id,
            name=campaign.name,
            slug=campaign.slug,
            description=campaign.description,
            banner_image_url=campaign.banner_image_url,
            landing_url=campaign.landing_url,
            badge_text=campaign.badge_text,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            is_active=campaign.is_active,
            priority=campaign.priority,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            message="Акция успешно найдена",
        )

    async def create_campaign(self, request: CampaignCreateRequest) -> CampaignResponse:
        if request.start_date >= request.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дата начала должна быть раньше даты окончания",
            )

        campaign = await self.repository.create_campaign(request)
        return CampaignResponse(
            id=campaign.id,
            name=campaign.name,
            slug=campaign.slug,
            description=campaign.description,
            banner_image_url=campaign.banner_image_url,
            landing_url=campaign.landing_url,
            badge_text=campaign.badge_text,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            is_active=campaign.is_active,
            priority=campaign.priority,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            message="Акция успешно создана",
        )

    async def update_campaign(
        self,
        campaign_id: int,
        request: CampaignUpdateRequest,
    ) -> CampaignResponse:
        existing = await self.repository.get_campaign_by_id(campaign_id, include_inactive=True)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Акция с id {campaign_id} не найдена",
            )

        start_date = request.start_date if request.start_date is not None else existing.start_date
        end_date = request.end_date if request.end_date is not None else existing.end_date
        if start_date >= end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дата начала должна быть раньше даты окончания",
            )

        campaign = await self.repository.update_campaign(campaign_id, request)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при обновлении акции",
            )

        return CampaignResponse(
            id=campaign.id,
            name=campaign.name,
            slug=campaign.slug,
            description=campaign.description,
            banner_image_url=campaign.banner_image_url,
            landing_url=campaign.landing_url,
            badge_text=campaign.badge_text,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            is_active=campaign.is_active,
            priority=campaign.priority,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            message="Акция успешно обновлена",
        )

    async def delete_campaign(self, campaign_id: int) -> CampaignDeleteResponse:
        success = await self.repository.deactivate_campaign(campaign_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Акция с id {campaign_id} не найдена",
            )

        return CampaignDeleteResponse(
            campaign_id=campaign_id,
            message="Акция успешно деактивирована",
        )

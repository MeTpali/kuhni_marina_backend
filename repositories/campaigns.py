from typing import List, Optional, Tuple
import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.campaigns import Campaign
from core.schemas.campaigns import CampaignCreateRequest, CampaignUpdateRequest
from core.utils.slug import generate_unique_slug

logger = logging.getLogger(__name__)


class CampaignRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_campaigns(
        self,
        page: int = 1,
        page_size: int = 20,
        include_inactive: bool = False,
    ) -> Tuple[List[Campaign], int]:
        logger.info(
            "Fetching campaigns: page=%s, page_size=%s, include_inactive=%s",
            page,
            page_size,
            include_inactive,
        )
        offset = (page - 1) * page_size

        query = select(Campaign)
        count_query = select(func.count(Campaign.id))
        if not include_inactive:
            query = query.where(Campaign.is_active.is_(True))
            count_query = count_query.where(Campaign.is_active.is_(True))

        query = query.order_by(Campaign.priority.desc(), Campaign.created_at.desc(), Campaign.id.desc())
        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)
        campaigns = result.scalars().all()

        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        return campaigns, total

    async def get_campaign_by_id(
        self,
        campaign_id: int,
        include_inactive: bool = False,
    ) -> Optional[Campaign]:
        query = select(Campaign).where(Campaign.id == campaign_id)
        if not include_inactive:
            query = query.where(Campaign.is_active.is_(True))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def generate_unique_slug(self, text: str, exclude_id: Optional[int] = None) -> str:
        """
        Генерирует уникальный slug для акции.
        """
        return await generate_unique_slug(self.session, Campaign, text, exclude_id)

    async def create_campaign(self, request: CampaignCreateRequest) -> Campaign:
        # Генерируем slug, если не передан (как в создании продукта)
        if request.slug is None or not request.slug.strip():
            slug = await self.generate_unique_slug(request.name)
        else:
            slug = await self.generate_unique_slug(request.slug)

        campaign = Campaign(
            name=request.name,
            slug=slug,
            description=request.description,
            banner_image_url=request.banner_image_url,
            landing_url=request.landing_url,
            badge_text=request.badge_text,
            start_date=request.start_date,
            end_date=request.end_date,
            is_active=request.is_active,
            priority=request.priority,
        )

        self.session.add(campaign)
        await self.session.commit()
        await self.session.refresh(campaign)
        return campaign

    async def update_campaign(
        self,
        campaign_id: int,
        request: CampaignUpdateRequest,
    ) -> Optional[Campaign]:
        campaign = await self.get_campaign_by_id(campaign_id, include_inactive=True)
        if campaign is None:
            return None

        if request.name is not None:
            campaign.name = request.name
        if request.slug is not None:
            campaign.slug = await self.generate_unique_slug(request.slug, exclude_id=campaign_id)
        elif request.name is not None:
            campaign.slug = await self.generate_unique_slug(request.name, exclude_id=campaign_id)
        if request.description is not None:
            campaign.description = request.description
        if request.banner_image_url is not None:
            campaign.banner_image_url = request.banner_image_url
        if request.landing_url is not None:
            campaign.landing_url = request.landing_url
        if request.badge_text is not None:
            campaign.badge_text = request.badge_text
        if request.start_date is not None:
            campaign.start_date = request.start_date
        if request.end_date is not None:
            campaign.end_date = request.end_date
        if request.is_active is not None:
            campaign.is_active = request.is_active
        if request.priority is not None:
            campaign.priority = request.priority

        await self.session.commit()
        await self.session.refresh(campaign)
        return campaign

    async def deactivate_campaign(self, campaign_id: int) -> bool:
        campaign = await self.get_campaign_by_id(campaign_id, include_inactive=True)
        if campaign is None:
            return False

        campaign.is_active = False
        await self.session.commit()
        return True

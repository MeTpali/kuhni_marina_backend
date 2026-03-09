from fastapi import APIRouter, Depends, Query, status

from api.deps import get_campaign_service
from services.campaigns import CampaignService
from core.schemas.campaigns import (
    CampaignCreateRequest,
    CampaignUpdateRequest,
    CampaignResponse,
    CampaignListResponse,
    CampaignDeleteResponse,
)

router = APIRouter(
    prefix="/campaigns",
    tags=["campaigns"],
    responses={404: {"description": "Campaign not found"}},
)


@router.get(
    "",
    response_model=CampaignListResponse,
    summary="Получить список акций",
    description="Возвращает список акций с пагинацией",
)
async def get_campaigns(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    include_inactive: bool = Query(False, description="Включить неактивные акции"),
    campaign_service: CampaignService = Depends(get_campaign_service),
):
    return await campaign_service.get_campaigns(
        page=page,
        page_size=page_size,
        include_inactive=include_inactive,
    )


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
    summary="Получить акцию по идентификатору",
    description="Возвращает акцию с указанным идентификатором",
)
async def get_campaign_by_id(
    campaign_id: int,
    campaign_service: CampaignService = Depends(get_campaign_service),
):
    return await campaign_service.get_campaign_by_id(campaign_id)


@router.post(
    "",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать акцию",
    description="Создает новую маркетинговую акцию (slug генерируется автоматически, если не передан)",
)
async def create_campaign(
    request: CampaignCreateRequest,
    campaign_service: CampaignService = Depends(get_campaign_service),
):
    return await campaign_service.create_campaign(request)


@router.put(
    "/{campaign_id}",
    response_model=CampaignResponse,
    summary="Обновить акцию",
    description="Обновляет акцию по идентификатору",
)
async def update_campaign(
    campaign_id: int,
    request: CampaignUpdateRequest,
    campaign_service: CampaignService = Depends(get_campaign_service),
):
    return await campaign_service.update_campaign(campaign_id, request)


@router.delete(
    "/{campaign_id}",
    response_model=CampaignDeleteResponse,
    summary="Удалить акцию",
    description="Деактивирует акцию по идентификатору",
)
async def delete_campaign(
    campaign_id: int,
    campaign_service: CampaignService = Depends(get_campaign_service),
):
    return await campaign_service.delete_campaign(campaign_id)

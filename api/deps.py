from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from repositories.attributes import AttributeRepository
from repositories.categories import CategoryRepository
from repositories.banners import BannerRepository
from repositories.measure_requests import MeasureRequestRepository

from services.attributes import AttributeService
from services.categories import CategoryService
from services.banners import BannerService
from services.measure_requests import MeasureRequestService

async def get_attribute_repository(
    db: AsyncSession = Depends(get_async_session),
) -> AttributeRepository:
    return AttributeRepository(db)


async def get_attribute_service(
    attribute_repository: AttributeRepository = Depends(get_attribute_repository),
) -> AttributeService:
    return AttributeService(attribute_repository)


async def get_category_repository(
    db: AsyncSession = Depends(get_async_session),
) -> CategoryRepository:
    return CategoryRepository(db)


async def get_category_service(
    category_repository: CategoryRepository = Depends(get_category_repository),
) -> CategoryService:
    return CategoryService(category_repository)


async def get_banner_repository(
    db: AsyncSession = Depends(get_async_session),
) -> BannerRepository:
    return BannerRepository(db)


async def get_banner_service(
    banner_repository: BannerRepository = Depends(get_banner_repository),
) -> BannerService:
    return BannerService(banner_repository)


async def get_measure_request_repository(
    db: AsyncSession = Depends(get_async_session),
) -> MeasureRequestRepository:
    return MeasureRequestRepository(db)


async def get_measure_request_service(
    measure_request_repository: MeasureRequestRepository = Depends(get_measure_request_repository),
) -> MeasureRequestService:
    return MeasureRequestService(measure_request_repository)

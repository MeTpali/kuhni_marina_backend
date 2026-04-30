from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from repositories.attributes import AttributeRepository
from repositories.categories import CategoryRepository
from repositories.products import ProductRepository
from repositories.banners import BannerRepository
from repositories.measure_requests import MeasureRequestRepository
from repositories.product_attributes import ProductAttributeRepository
from repositories.product_images import ProductImageRepository
from repositories.project_products import ProjectProductRepository
from repositories.project_images import ProjectImageRepository
from repositories.projects import ProjectRepository
from repositories.reviews import ReviewRepository
from repositories.discounts import DiscountRepository
from repositories.campaigns import CampaignRepository
from repositories.background_images import BackgroundImageRepository

from services.attributes import AttributeService
from services.categories import CategoryService
from services.products import ProductService
from services.banners import BannerService
from services.measure_requests import MeasureRequestService
from services.product_attributes import ProductAttributeService
from services.product_images import ProductImageService
from services.project_products import ProjectProductService
from services.project_images import ProjectImageService
from services.projects import ProjectService
from services.reviews import ReviewService
from services.discounts import DiscountService
from services.campaigns import CampaignService
from services.background_images import BackgroundImageService


def get_guest_session_id(request: Request) -> UUID:
    """UUID активной гостевой сессии (ставит GuestSessionMiddleware)."""
    sid = getattr(request.state, "guest_session_id", None)
    if sid is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Гостевая сессия недоступна для этого маршрута",
        )
    return sid


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


async def get_product_repository(
    db: AsyncSession = Depends(get_async_session),
) -> ProductRepository:
    return ProductRepository(db)


async def get_product_service(
    product_repository: ProductRepository = Depends(get_product_repository),
) -> ProductService:
    return ProductService(product_repository)


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


async def get_product_attribute_repository(
    db: AsyncSession = Depends(get_async_session),
) -> ProductAttributeRepository:
    return ProductAttributeRepository(db)


async def get_product_attribute_service(
    product_attribute_repository: ProductAttributeRepository = Depends(get_product_attribute_repository),
) -> ProductAttributeService:
    return ProductAttributeService(product_attribute_repository)


async def get_product_image_repository(
    db: AsyncSession = Depends(get_async_session),
) -> ProductImageRepository:
    return ProductImageRepository(db)


async def get_product_image_service(
    product_image_repository: ProductImageRepository = Depends(get_product_image_repository),
) -> ProductImageService:
    return ProductImageService(product_image_repository)


async def get_project_product_repository(
    db: AsyncSession = Depends(get_async_session),
) -> ProjectProductRepository:
    return ProjectProductRepository(db)


async def get_project_product_service(
    project_product_repository: ProjectProductRepository = Depends(get_project_product_repository),
) -> ProjectProductService:
    return ProjectProductService(project_product_repository)


async def get_project_image_repository(
    db: AsyncSession = Depends(get_async_session),
) -> ProjectImageRepository:
    return ProjectImageRepository(db)


async def get_project_image_service(
    project_image_repository: ProjectImageRepository = Depends(get_project_image_repository),
) -> ProjectImageService:
    return ProjectImageService(project_image_repository)


async def get_review_repository(
    db: AsyncSession = Depends(get_async_session),
) -> ReviewRepository:
    return ReviewRepository(db)


async def get_review_service(
    review_repository: ReviewRepository = Depends(get_review_repository),
) -> ReviewService:
    return ReviewService(review_repository)


async def get_project_repository(
    db: AsyncSession = Depends(get_async_session),
) -> ProjectRepository:
    return ProjectRepository(db)


async def get_project_service(
    project_repository: ProjectRepository = Depends(get_project_repository),
    project_image_repository: ProjectImageRepository = Depends(get_project_image_repository),
    project_product_repository: ProjectProductRepository = Depends(get_project_product_repository),
) -> ProjectService:
    return ProjectService(project_repository, project_image_repository, project_product_repository)


async def get_discount_repository(
    db: AsyncSession = Depends(get_async_session),
) -> DiscountRepository:
    return DiscountRepository(db)


async def get_discount_service(
    discount_repository: DiscountRepository = Depends(get_discount_repository),
) -> DiscountService:
    return DiscountService(discount_repository)


async def get_campaign_repository(
    db: AsyncSession = Depends(get_async_session),
) -> CampaignRepository:
    return CampaignRepository(db)


async def get_campaign_service(
    campaign_repository: CampaignRepository = Depends(get_campaign_repository),
) -> CampaignService:
    return CampaignService(campaign_repository)


async def get_background_image_repository(
    db: AsyncSession = Depends(get_async_session),
) -> BackgroundImageRepository:
    return BackgroundImageRepository(db)


async def get_background_image_service(
    background_image_repository: BackgroundImageRepository = Depends(get_background_image_repository),
) -> BackgroundImageService:
    return BackgroundImageService(background_image_repository)

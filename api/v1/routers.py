from fastapi import APIRouter
from api.v1.endpoints import (
    attributes,
    categories,
    session,
    products,
    banners,
    measure_requests,
    product_attributes,
    product_images,
    project_images,
    projects,
    reviews,
    discounts,
    campaigns,
    background_images,
)

api_router = APIRouter()

api_router.include_router(attributes.router)
api_router.include_router(categories.router)
api_router.include_router(session.router)
api_router.include_router(products.router)
api_router.include_router(banners.router)
api_router.include_router(measure_requests.router)
api_router.include_router(product_attributes.router)
api_router.include_router(product_images.router)
api_router.include_router(project_images.router)
api_router.include_router(projects.router)
api_router.include_router(reviews.router)
api_router.include_router(discounts.router)
api_router.include_router(campaigns.router)
api_router.include_router(background_images.router)
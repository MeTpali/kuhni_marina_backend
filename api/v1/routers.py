from fastapi import APIRouter
from api.v1.endpoints import (
    attributes,
    categories,
    banners,
    measure_requests,
)

api_router = APIRouter()

api_router.include_router(attributes.router)
api_router.include_router(categories.router)
api_router.include_router(banners.router)
api_router.include_router(measure_requests.router)
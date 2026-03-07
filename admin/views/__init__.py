"""
Все ModelView и BaseView админки.
"""
from admin.views.attributes import AttributeAdmin
from admin.views.banners import BannerAdmin
from admin.views.categories import CategoryAdmin
from admin.views.discounts import DiscountAdmin
from admin.views.measure_requests import MeasureRequestAdmin
from admin.views.product_attributes import ProductAttributeAdmin
from admin.views.product_images import BulkProductImagesAdmin, ProductImageAdmin
from admin.views.products import ProductAdmin
from admin.views.projects import (
    BulkProjectImagesAdmin,
    ProjectAdmin,
    ProjectImageAdmin,
    ProjectProductAdmin,
)
from admin.views.reviews import ReviewAdmin

__all__ = [
    "AttributeAdmin",
    "BannerAdmin",
    "BulkProductImagesAdmin",
    "BulkProjectImagesAdmin",
    "CategoryAdmin",
    "DiscountAdmin",
    "MeasureRequestAdmin",
    "ProductAdmin",
    "ProductAttributeAdmin",
    "ProductImageAdmin",
    "ProjectAdmin",
    "ProjectImageAdmin",
    "ProjectProductAdmin",
    "ReviewAdmin",
]

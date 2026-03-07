"""
Пакет админ-панели. Точка входа: setup_admin(app).
"""
import os

from fastapi import FastAPI
from sqladmin import Admin

from core.config import settings
from core.models.db_helper import db_helper

from admin.auth import AdminAuth
from admin.views import (
    AttributeAdmin,
    BannerAdmin,
    BulkProductImagesAdmin,
    BulkProjectImagesAdmin,
    CategoryAdmin,
    DiscountAdmin,
    MeasureRequestAdmin,
    ProductAdmin,
    ProductAttributeAdmin,
    ProductImageAdmin,
    ProjectAdmin,
    ProjectImageAdmin,
    ProjectProductAdmin,
    ReviewAdmin,
)


def setup_admin(app: FastAPI) -> Admin:
    """
    Настройка SQLAdmin для приложения. Регистрирует все представления и возвращает экземпляр Admin.
    """
    authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
    _dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(_dir, "templates")

    admin = Admin(
        app,
        engine=db_helper.engine,
        title="Админ-панель - Кухни Вязники",
        base_url="/admin",
        authentication_backend=authentication_backend,
        templates_dir=templates_dir,
    )

    admin.add_view(CategoryAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(AttributeAdmin)
    admin.add_view(ProductImageAdmin)
    admin.add_view(BulkProductImagesAdmin)
    admin.add_view(ProductAttributeAdmin)
    admin.add_view(ReviewAdmin)
    admin.add_view(ProjectAdmin)
    admin.add_view(ProjectImageAdmin)
    admin.add_view(BulkProjectImagesAdmin)
    admin.add_view(ProjectProductAdmin)
    admin.add_view(BannerAdmin)
    admin.add_view(DiscountAdmin)
    admin.add_view(MeasureRequestAdmin)

    return admin

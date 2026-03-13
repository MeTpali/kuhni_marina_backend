import asyncio

from fastapi import Request
from sqladmin import ModelView
from sqladmin.fields import FileField
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.banners import Banner
from core.models.db_helper import db_helper
from core.storage import upload_banner_image


def _is_upload_file(obj) -> bool:
    return obj is not None and hasattr(obj, "read") and getattr(obj, "filename", None)


async def _banner_image_from_file(data: dict) -> None:
    """Если в data есть загруженный файл image_file — заливает в Yandex Object Storage и подставляет URL в image_url."""
    f = data.pop("image_file", None)
    if not _is_upload_file(f):
        return
    body = await f.read()
    content_type = getattr(f, "content_type", None) or ""
    filename = getattr(f, "filename", None)
    url = await asyncio.to_thread(
        upload_banner_image,
        body,
        content_type or None,
        filename,
    )
    data["image_url"] = url


class BannerAdmin(ModelView, model=Banner):
    name = "Баннер"
    name_plural = "Баннеры"
    icon = "fa-solid fa-image"
    column_list = [Banner.id, Banner.title, Banner.priority, Banner.is_active]
    column_details_list = [Banner.id, Banner.title, Banner.image_url, Banner.link_url, Banner.priority, Banner.is_active]
    column_searchable_list = [Banner.title]
    column_sortable_list = [Banner.id, Banner.priority]
    column_labels = {
        Banner.id: "ID",
        Banner.title: "Заголовок",
        Banner.image_url: "URL изображения",
        Banner.link_url: "URL ссылки",
        Banner.priority: "Приоритет",
        Banner.is_active: "Активен",
    }
    # В форме только загрузка файла — URL подставляется из Yandex Object Storage при сохранении
    form_columns = [Banner.title, Banner.link_url, Banner.priority, Banner.is_active]
    form_args = {
        "link_url": {"validators": []},
    }

    async def scaffold_form(self, rules=None):
        form_class = await super().scaffold_form(rules)
        class FormWithFile(form_class):
            image_file = FileField("Изображение баннера (файл)")
        return FormWithFile

    async def insert_model(self, request: Request, data: dict) -> Banner:
        await _banner_image_from_file(data)
        if not (data.get("image_url") or "").strip():
            raise ValueError("Загрузите файл изображения.")
        return await super().insert_model(request, data)

    async def update_model(self, request: Request, pk: str, data: dict) -> Banner:
        await _banner_image_from_file(data)
        # Если ни файл не загружен, ни URL не указан — оставляем текущее изображение баннера
        if not (data.get("image_url") or "").strip():
            async with AsyncSession(bind=db_helper.engine) as session:
                result = await session.execute(select(Banner).where(Banner.id == int(pk)))
                banner = result.scalar_one_or_none()
                if banner and banner.image_url:
                    data["image_url"] = banner.image_url
        return await super().update_model(request, pk, data)

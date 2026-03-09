import asyncio

from fastapi import Request
from sqladmin import ModelView
from sqladmin.fields import FileField

from core.models.banners import Banner
from core.storage import upload_banner_image


def _is_upload_file(obj) -> bool:
    return obj is not None and hasattr(obj, "read") and getattr(obj, "filename", None)


async def _banner_image_from_file(data: dict) -> None:
    """Если в data есть загруженный файл image_file — заливает в облако и подставляет URL в image_url."""
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
    column_list = [Banner.id, Banner.title, Banner.position, Banner.is_active]
    column_details_list = [Banner.id, Banner.title, Banner.image_url, Banner.link_url, Banner.position, Banner.is_active]
    column_searchable_list = [Banner.title]
    column_sortable_list = [Banner.id, Banner.position]
    column_labels = {
        Banner.id: "ID",
        Banner.title: "Заголовок",
        Banner.image_url: "URL изображения",
        Banner.link_url: "URL ссылки",
        Banner.position: "Позиция",
        Banner.is_active: "Активен",
    }
    form_columns = [Banner.title, Banner.image_url, Banner.link_url, Banner.position, Banner.is_active]
    form_args = {
        "image_url": {"validators": []},  # можно оставить пустым, если загружаете файл
    }

    async def scaffold_form(self, rules=None):
        form_class = await super().scaffold_form(rules)
        # SQLAdmin не поддерживает form_extra_fields — добавляем поле файла вручную
        class FormWithFile(form_class):
            image_file = FileField("Загрузить изображение (файл)")
        return FormWithFile

    async def insert_model(self, request: Request, data: dict) -> Banner:
        await _banner_image_from_file(data)
        if not (data.get("image_url") or "").strip():
            raise ValueError("Укажите URL изображения или загрузите файл.")
        return await super().insert_model(request, data)

    async def update_model(self, request: Request, pk: str, data: dict) -> Banner:
        await _banner_image_from_file(data)
        return await super().update_model(request, pk, data)

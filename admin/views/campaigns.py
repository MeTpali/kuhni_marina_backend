import asyncio

from fastapi import Request
from sqladmin import ModelView
from sqladmin.fields import FileField
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.db_helper import db_helper
from core.models.campaigns import Campaign
from core.storage import upload_campaign_image
from core.utils.slug import generate_unique_slug


def _is_upload_file(obj) -> bool:
    return obj is not None and hasattr(obj, "read") and getattr(obj, "filename", None)


async def _campaign_banner_image_from_file(data: dict) -> None:
    """Если в data есть загруженный файл banner_image_file — заливает в облако и подставляет URL в banner_image_url."""
    f = data.pop("banner_image_file", None)
    if not _is_upload_file(f):
        return
    body = await f.read()
    content_type = getattr(f, "content_type", None) or ""
    filename = getattr(f, "filename", None)
    url = await asyncio.to_thread(
        upload_campaign_image,
        body,
        content_type or None,
        filename,
    )
    data["banner_image_url"] = url


class CampaignAdmin(ModelView, model=Campaign):
    name = "Акция"
    name_plural = "Акции"
    icon = "fa-solid fa-bullhorn"

    column_list = [
        Campaign.id,
        Campaign.name,
        Campaign.slug,
        Campaign.start_date,
        Campaign.end_date,
        Campaign.priority,
        Campaign.is_active,
    ]
    column_details_list = [
        Campaign.id,
        Campaign.name,
        Campaign.slug,
        Campaign.description,
        Campaign.banner_image_url,
        Campaign.landing_url,
        Campaign.badge_text,
        Campaign.start_date,
        Campaign.end_date,
        Campaign.priority,
        Campaign.is_active,
        Campaign.created_at,
        Campaign.updated_at,
    ]
    column_searchable_list = [Campaign.name, Campaign.slug]
    column_sortable_list = [
        Campaign.id,
        Campaign.name,
        Campaign.priority,
        Campaign.start_date,
        Campaign.end_date,
        Campaign.created_at,
    ]
    column_labels = {
        Campaign.id: "ID",
        Campaign.name: "Название",
        Campaign.slug: "Slug",
        Campaign.description: "Описание",
        Campaign.banner_image_url: "URL баннера",
        Campaign.landing_url: "Landing URL",
        Campaign.badge_text: "Бейдж",
        Campaign.start_date: "Дата начала",
        Campaign.end_date: "Дата окончания",
        Campaign.priority: "Приоритет",
        Campaign.is_active: "Активна",
        Campaign.created_at: "Дата создания",
        Campaign.updated_at: "Дата обновления",
    }
    form_columns = [
        Campaign.name,
        Campaign.description,
        Campaign.banner_image_url,
        Campaign.landing_url,
        Campaign.badge_text,
        Campaign.start_date,
        Campaign.end_date,
        Campaign.priority,
        Campaign.is_active,
    ]

    async def scaffold_form(self, rules=None):
        form_class = await super().scaffold_form(rules)
        # SQLAdmin не поддерживает form_extra_fields — добавляем поле файла вручную
        class FormWithFile(form_class):
            banner_image_file = FileField("Загрузить изображение баннера (файл)")
        return FormWithFile

    async def insert_model(self, request: Request, data: dict) -> Campaign:
        await _campaign_banner_image_from_file(data)
        if not data.get("slug") or not str(data.get("slug")).strip():
            name = data.get("name", "")
            if name:
                async with AsyncSession(bind=db_helper.engine) as session:
                    await session.execute(text("SET search_path TO kuhni_marina, public"))
                    slug = await generate_unique_slug(session, Campaign, name)
                    data["slug"] = slug
        return await super().insert_model(request, data)

    async def update_model(self, request: Request, pk: int, data: dict) -> Campaign:
        await _campaign_banner_image_from_file(data)
        async with AsyncSession(bind=db_helper.engine) as session:
            await session.execute(text("SET search_path TO kuhni_marina, public"))
            result = await session.execute(select(Campaign).where(Campaign.id == pk))
            current_campaign = result.scalar_one_or_none()
            if current_campaign:
                if "name" in data and data["name"] != current_campaign.name:
                    if "slug" not in data or not data.get("slug") or not str(data.get("slug")).strip():
                        slug = await generate_unique_slug(session, Campaign, data["name"], exclude_id=pk)
                        data["slug"] = slug
                elif "slug" in data and data.get("slug"):
                    slug = await generate_unique_slug(session, Campaign, data["slug"], exclude_id=pk)
                    data["slug"] = slug
        return await super().update_model(request, pk, data)

from fastapi import Request
from sqladmin import ModelView
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.db_helper import db_helper
from core.models.products import Product, ProductType
from core.utils.slug import generate_unique_slug


class ProductAdmin(ModelView, model=Product):
    name = "Продукт"
    name_plural = "Продукты"
    icon = "fa-solid fa-box"
    column_list = [Product.id, Product.name, Product.slug, Product.category_id, Product.price, Product.type, Product.is_active, Product.created_at]
    column_details_list = [Product.id, Product.name, Product.slug, Product.category_id, Product.description, Product.price, Product.is_new, Product.is_hit, Product.type, Product.is_active, Product.created_at, Product.updated_at, Product.discounts]
    column_searchable_list = [Product.name, Product.slug, Product.description]
    column_sortable_list = [Product.id, Product.name, Product.price, Product.created_at]
    column_labels = {
        Product.id: "ID",
        Product.name: "Название",
        Product.slug: "Slug",
        Product.category_id: "Категория",
        Product.description: "Описание",
        Product.price: "Цена",
        Product.is_new: "Новинка",
        Product.is_hit: "Хит продаж",
        Product.type: "Тип",
        Product.is_active: "Активен",
        Product.created_at: "Дата создания",
        Product.updated_at: "Дата обновления",
        Product.discounts: "Скидки",
    }
    form_columns = [Product.name, Product.category, Product.description, Product.price, Product.is_new, Product.is_hit, Product.type, Product.is_active]
    form_ajax_refs = {
        "category": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }
    form_args = {
        "type": {
            "choices": [(prod_type.value, prod_type.name) for prod_type in ProductType],
        }
    }

    async def insert_model(self, request: Request, data: dict) -> Product:
        if not data.get("slug") or not str(data.get("slug")).strip():
            name = data.get("name", "")
            if name:
                async with AsyncSession(bind=db_helper.engine) as session:
                    await session.execute(text("SET search_path TO kuhni_marina, public"))
                    slug = await generate_unique_slug(session, Product, name)
                    data["slug"] = slug
        return await super().insert_model(request, data)

    async def update_model(self, request: Request, pk: int, data: dict) -> Product:
        async with AsyncSession(bind=db_helper.engine) as session:
            await session.execute(text("SET search_path TO kuhni_marina, public"))
            result = await session.execute(select(Product).where(Product.id == pk))
            current_product = result.scalar_one_or_none()
            if current_product:
                if "name" in data and data["name"] != current_product.name:
                    if "slug" not in data or not data.get("slug") or not str(data.get("slug")).strip():
                        slug = await generate_unique_slug(session, Product, data["name"], exclude_id=pk)
                        data["slug"] = slug
                elif "slug" in data and data.get("slug"):
                    slug = await generate_unique_slug(session, Product, data["slug"], exclude_id=pk)
                    data["slug"] = slug
        return await super().update_model(request, pk, data)

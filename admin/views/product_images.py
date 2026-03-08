from urllib.parse import quote

from fastapi import Request
from sqladmin import BaseView, ModelView, expose
from sqladmin.filters import OperationColumnFilter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

import asyncio

from admin.bulk_assets import bulk_images_html
from admin.helpers import with_image_session
from core.models.product_images import ProductImage
from core.storage import upload_product_image as storage_upload_product_image
from core.models.products import Product
from repositories.product_images import ProductImageRepository


class ProductImageAdmin(ModelView, model=ProductImage):
    name = "Изображение продукта"
    name_plural = "Изображения продуктов"
    icon = "fa-solid fa-image"
    column_list = [ProductImage.id, ProductImage.product_id, ProductImage.image_url, ProductImage.is_main]
    column_details_list = [ProductImage.id, ProductImage.product_id, ProductImage.image_url, ProductImage.is_main]
    column_searchable_list = [ProductImage.image_url]
    column_sortable_list = [ProductImage.id, ProductImage.product_id]
    column_filters = [
        OperationColumnFilter(ProductImage.product_id, title="ID продукта"),
        OperationColumnFilter(ProductImage.image_url, title="URL изображения"),
    ]
    column_labels = {
        ProductImage.id: "ID",
        ProductImage.product_id: "Продукт",
        ProductImage.image_url: "URL изображения",
        ProductImage.is_main: "Главное",
    }
    form_columns = [ProductImage.product, ProductImage.image_url, ProductImage.is_main]
    form_ajax_refs = {
        "product": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }

    def _get_product_id_from_data(self, data: dict) -> int | None:
        pid = data.get("product_id")
        if pid is not None:
            return int(pid) if isinstance(pid, (int, str)) else None
        p = data.get("product")
        if p is not None and hasattr(p, "id"):
            return p.id
        return None

    async def insert_model(self, request: Request, data: dict) -> ProductImage:
        product_id = self._get_product_id_from_data(data)
        if product_id is not None:
            async def _check_first(session: AsyncSession):
                repo = ProductImageRepository(session)
                existing = await repo.get_product_images_by_product_id(product_id)
                if len(existing) == 0:
                    data["is_main"] = True
            await with_image_session(_check_first)
        result = await super().insert_model(request, data)
        if result and result.is_main and product_id is not None:
            async def _ensure(session: AsyncSession):
                repo = ProductImageRepository(session)
                await repo.ensure_single_main_for_product(product_id, result.id)
            await with_image_session(_ensure)
        return result

    async def update_model(self, request: Request, pk: int, data: dict) -> ProductImage:
        result = await super().update_model(request, pk, data)
        if result and data.get("is_main") is True:
            async def _ensure(session: AsyncSession):
                repo = ProductImageRepository(session)
                img = await repo.get_product_image_by_id(pk)
                if img:
                    await repo.ensure_single_main_for_product(img.product_id, pk)
            await with_image_session(_ensure)
        return result

    async def delete_model(self, request: Request, pk: int) -> None:
        product_id = None
        was_main = False

        async def _load(session: AsyncSession):
            nonlocal product_id, was_main
            repo = ProductImageRepository(session)
            img = await repo.get_product_image_by_id(pk)
            if img:
                product_id = img.product_id
                was_main = img.is_main
        await with_image_session(_load)
        await super().delete_model(request, pk)
        if was_main and product_id is not None:
            async def _promote(session: AsyncSession):
                repo = ProductImageRepository(session)
                remaining = await repo.get_product_images_by_product_id(product_id)
                if remaining:
                    await repo.ensure_single_main_for_product(product_id, remaining[0].id)
            await with_image_session(_promote)


class BulkProductImagesAdmin(BaseView):
    name = "Добавить несколько изображений продукта"
    icon = "fa-solid fa-images"

    @expose("/bulk-product-images/search", methods=["GET"])
    async def bulk_product_images_search(self, request: Request):
        q = (request.query_params.get("q") or "").strip()[:100]
        async def _search(session: AsyncSession):
            stmt = select(Product.id, Product.name).order_by(Product.name)
            if q:
                stmt = stmt.where(Product.name.ilike(f"%{q}%"))
            stmt = stmt.limit(50)
            result = await session.execute(stmt)
            return [{"id": r.id, "name": r.name} for r in result.all()]
        items = await with_image_session(_search)
        return JSONResponse(items)

    @expose("/bulk-product-images", methods=["GET", "POST"])
    async def bulk_product_images(self, request: Request):
        base_path = "/admin/bulk-product-images"
        if request.method == "POST":
            form = await request.form()
            product_id_str = (form.get("product_id") or "").strip()
            main_index_str = (form.get("main_index") or "").strip()
            if not product_id_str:
                return RedirectResponse(base_path + "?error=Выберите+продукт", status_code=303)
            try:
                product_id = int(product_id_str)
            except ValueError:
                return RedirectResponse(base_path + "?error=Некорректный+продукт", status_code=303)
            main_index = None
            if main_index_str:
                try:
                    main_index = int(main_index_str)
                except ValueError:
                    pass
            # Список файлов: multipart может отдать один или несколько под ключом "images"
            files = form.getlist("images") if hasattr(form, "getlist") else []
            if not files:
                return RedirectResponse(base_path + "?error=Выберите+хотя+бы+один+файл", status_code=303)
            image_urls = []
            for f in files:
                if getattr(f, "filename", None) is None or not getattr(f, "read", None):
                    continue
                try:
                    data = await f.read()
                    content_type = getattr(f, "content_type", None) or ""
                    filename = getattr(f, "filename", None)
                    url = await asyncio.to_thread(
                        storage_upload_product_image,
                        product_id,
                        data,
                        content_type or None,
                        filename,
                    )
                    image_urls.append(url)
                except ValueError as e:
                    return RedirectResponse(base_path + "?error=" + quote(str(e)), status_code=303)
            if not image_urls:
                return RedirectResponse(base_path + "?error=Нет+допустимых+изображений", status_code=303)
            async def _add(session: AsyncSession):
                repo = ProductImageRepository(session)
                return await repo.add_product_images(product_id, image_urls, main_index)
            created = await with_image_session(_add)
            return RedirectResponse(base_path + "?success=" + quote(f"Добавлено изображений: {len(created)}"), status_code=303)
        error = request.query_params.get("error", "")
        success = request.query_params.get("success", "")
        html = bulk_images_html(
            title="Массовое добавление изображений продукта",
            subtitle="Новые изображения будут добавлены к уже существующим у продукта.",
            entity_label="Продукт",
            search_placeholder="Введите название или часть названия продукта...",
            search_api_url=base_path + "/search",
            input_id="product_search",
            hidden_name="product_id",
            error=error,
            success=success,
        )
        return HTMLResponse(html)

    def is_visible(self, request: Request) -> bool:
        return True

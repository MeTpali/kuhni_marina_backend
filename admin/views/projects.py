import asyncio
from urllib.parse import quote

from fastapi import Request
from sqladmin import BaseView, ModelView, expose
from sqladmin.filters import OperationColumnFilter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

from admin.bulk_assets import bulk_images_html
from admin.helpers import with_image_session
from core.models.project_images import ProjectImage
from core.models.projects import Project
from core.storage import upload_project_image as storage_upload_project_image
from core.models.project_products import ProjectProduct
from repositories.project_images import ProjectImageRepository


class ProjectAdmin(ModelView, model=Project):
    name = "Проект"
    name_plural = "Проекты"
    icon = "fa-solid fa-folder-open"
    column_list = [Project.id, Project.name, Project.location, Project.created_at]
    column_details_list = [Project.id, Project.name, Project.description, Project.location, Project.created_at]
    column_searchable_list = [Project.name, Project.description, Project.location]
    column_sortable_list = [Project.id, Project.name, Project.created_at]
    column_labels = {
        Project.id: "ID",
        Project.name: "Название",
        Project.description: "Описание",
        Project.location: "Местоположение",
        Project.created_at: "Дата создания",
    }
    form_columns = [Project.name, Project.description, Project.location]


class ProjectImageAdmin(ModelView, model=ProjectImage):
    name = "Изображение проекта"
    name_plural = "Изображения проектов"
    icon = "fa-solid fa-images"
    column_list = [ProjectImage.id, ProjectImage.project_id, ProjectImage.image_url, ProjectImage.is_main]
    column_details_list = [ProjectImage.id, ProjectImage.project_id, ProjectImage.image_url, ProjectImage.is_main]
    column_searchable_list = [ProjectImage.image_url]
    column_sortable_list = [ProjectImage.id, ProjectImage.project_id]
    column_filters = [
        OperationColumnFilter(ProjectImage.project_id, title="ID проекта"),
        OperationColumnFilter(ProjectImage.image_url, title="URL изображения"),
    ]
    column_labels = {
        ProjectImage.id: "ID",
        ProjectImage.project_id: "Проект",
        ProjectImage.image_url: "URL изображения",
        ProjectImage.is_main: "Главное",
    }
    form_columns = [ProjectImage.project, ProjectImage.image_url, ProjectImage.is_main]
    form_ajax_refs = {
        "project": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }

    def _get_project_id_from_data(self, data: dict) -> int | None:
        pid = data.get("project_id")
        if pid is not None:
            return int(pid) if isinstance(pid, (int, str)) else None
        p = data.get("project")
        if p is not None and hasattr(p, "id"):
            return p.id
        return None

    async def insert_model(self, request: Request, data: dict) -> ProjectImage:
        project_id = self._get_project_id_from_data(data)
        if project_id is not None:
            async def _check_first(session: AsyncSession):
                repo = ProjectImageRepository(session)
                existing = await repo.get_project_images_by_project_id(project_id)
                if len(existing) == 0:
                    data["is_main"] = True
            await with_image_session(_check_first)
        result = await super().insert_model(request, data)
        if result and result.is_main and project_id is not None:
            async def _ensure(session: AsyncSession):
                repo = ProjectImageRepository(session)
                await repo.ensure_single_main_for_project(project_id, result.id)
            await with_image_session(_ensure)
        return result

    async def update_model(self, request: Request, pk: int, data: dict) -> ProjectImage:
        result = await super().update_model(request, pk, data)
        if result and data.get("is_main") is True:
            async def _ensure(session: AsyncSession):
                repo = ProjectImageRepository(session)
                img = await repo.get_project_image_by_id(pk)
                if img:
                    await repo.ensure_single_main_for_project(img.project_id, pk)
            await with_image_session(_ensure)
        return result

    async def delete_model(self, request: Request, pk: int) -> None:
        project_id = None
        was_main = False
        async def _load(session: AsyncSession):
            nonlocal project_id, was_main
            repo = ProjectImageRepository(session)
            img = await repo.get_project_image_by_id(pk)
            if img:
                project_id = img.project_id
                was_main = img.is_main
        await with_image_session(_load)
        await super().delete_model(request, pk)
        if was_main and project_id is not None:
            async def _promote(session: AsyncSession):
                repo = ProjectImageRepository(session)
                remaining = await repo.get_project_images_by_project_id(project_id)
                if remaining:
                    await repo.ensure_single_main_for_project(project_id, remaining[0].id)
            await with_image_session(_promote)


class BulkProjectImagesAdmin(BaseView):
    name = "Добавить несколько изображений проекта"
    icon = "fa-solid fa-images"

    @expose("/bulk-project-images/search", methods=["GET"])
    async def bulk_project_images_search(self, request: Request):
        q = (request.query_params.get("q") or "").strip()[:100]
        async def _search(session: AsyncSession):
            stmt = select(Project.id, Project.name).order_by(Project.name)
            if q:
                stmt = stmt.where(Project.name.ilike(f"%{q}%"))
            stmt = stmt.limit(50)
            result = await session.execute(stmt)
            return [{"id": r.id, "name": r.name} for r in result.all()]
        items = await with_image_session(_search)
        return JSONResponse(items)

    @expose("/bulk-project-images", methods=["GET", "POST"])
    async def bulk_project_images(self, request: Request):
        base_path = "/admin/bulk-project-images"
        if request.method == "POST":
            form = await request.form()
            project_id_str = (form.get("project_id") or "").strip()
            main_index_str = (form.get("main_index") or "").strip()
            if not project_id_str:
                return RedirectResponse(base_path + "?error=Выберите+проект", status_code=303)
            try:
                project_id = int(project_id_str)
            except ValueError:
                return RedirectResponse(base_path + "?error=Некорректный+проект", status_code=303)
            main_index = None
            if main_index_str:
                try:
                    main_index = int(main_index_str)
                except ValueError:
                    pass
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
                        storage_upload_project_image,
                        project_id,
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
                repo = ProjectImageRepository(session)
                return await repo.add_project_images(project_id, image_urls, main_index)
            created = await with_image_session(_add)
            return RedirectResponse(base_path + "?success=" + quote(f"Добавлено изображений: {len(created)}"), status_code=303)
        error = request.query_params.get("error", "")
        success = request.query_params.get("success", "")
        html = bulk_images_html(
            title="Массовое добавление изображений проекта",
            subtitle="Новые изображения будут добавлены к уже существующим у проекта.",
            entity_label="Проект",
            search_placeholder="Введите название или часть названия проекта...",
            search_api_url=base_path + "/search",
            input_id="project_search",
            hidden_name="project_id",
            error=error,
            success=success,
        )
        return HTMLResponse(html)

    def is_visible(self, request: Request) -> bool:
        return True


class ProjectProductAdmin(ModelView, model=ProjectProduct):
    name = "Продукт в проекте"
    name_plural = "Продукты в проектах"
    icon = "fa-solid fa-link"
    column_list = [ProjectProduct.project_id, ProjectProduct.product_id]
    column_details_list = [ProjectProduct.project_id, ProjectProduct.product_id]
    column_sortable_list = [ProjectProduct.project_id, ProjectProduct.product_id]
    column_labels = {
        ProjectProduct.project_id: "Проект",
        ProjectProduct.product_id: "Продукт",
    }
    form_columns = [ProjectProduct.project, ProjectProduct.product]
    form_ajax_refs = {
        "project": {
            "fields": ("name", "id"),
            "order_by": "name",
        },
        "product": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }

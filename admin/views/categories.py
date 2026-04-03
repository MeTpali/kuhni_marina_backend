import asyncio

from fastapi import Request
from sqladmin import ModelView, expose
from sqladmin.fields import FileField
from starlette.responses import JSONResponse

from admin.helpers import with_image_session
from core.models.categories import Category, CategoryType
from core.storage import upload_category_image
from repositories.categories import CategoryRepository


def _is_upload_file(obj) -> bool:
    return obj is not None and hasattr(obj, "read") and getattr(obj, "filename", None)


async def _category_image_from_file(data: dict) -> None:
    """Если в data есть загруженный файл image_file — заливает в Yandex Object Storage и подставляет URL в image_url."""
    f = data.pop("image_file", None)
    if not _is_upload_file(f):
        return
    body = await f.read()
    content_type = getattr(f, "content_type", None) or ""
    filename = getattr(f, "filename", None)
    url = await asyncio.to_thread(
        upload_category_image,
        body,
        content_type or None,
        filename,
    )
    data["image_url"] = url


class CategoryAdmin(ModelView, model=Category):
    name = "Категория"
    name_plural = "Категории"
    icon = "fa-solid fa-folder"
    column_list = [Category.id, Category.name, Category.slug, Category.type, Category.parent_id, Category.image_url, Category.is_active, Category.created_at]
    column_details_list = [Category.id, Category.name, Category.slug, Category.type, Category.parent_id, Category.image_url, Category.is_active, Category.created_at]
    column_searchable_list = [Category.name, Category.slug]
    column_sortable_list = [Category.id, Category.name, Category.created_at]
    column_labels = {
        Category.id: "ID",
        Category.name: "Название",
        Category.slug: "Slug",
        Category.type: "Тип",
        Category.parent_id: "Родительская категория",
        Category.image_url: "URL изображения",
        Category.is_active: "Активна",
        Category.created_at: "Дата создания",
    }
    form_columns = [Category.name, Category.slug, Category.type, Category.parent, Category.image_url, Category.is_active]
    form_ajax_refs = {
        "parent": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }
    form_args = {
        "type": {
            "choices": [(cat_type.value, cat_type.name) for cat_type in CategoryType],
        },
        "image_url": {"validators": []},
    }

    async def scaffold_form(self, rules=None):
        form_class = await super().scaffold_form(rules)
        class FormWithFile(form_class):
            image_file = FileField("Загрузить изображение категории (файл)")
        return FormWithFile

    async def insert_model(self, request: Request, data: dict) -> Category:
        await _category_image_from_file(data)
        return await super().insert_model(request, data)

    async def update_model(self, request: Request, pk: str, data: dict) -> Category:
        await _category_image_from_file(data)
        return await super().update_model(request, pk, data)

    @staticmethod
    def _build_tree_payload(items: list[dict]) -> list[dict]:
        nodes: dict[int, dict] = {}
        roots: list[dict] = []

        for item in items:
            node = {
                "id": item["id"],
                "name": item["name"],
                "parent_id": item["parent_id"],
                "type": item["type"],
                "image_url": item.get("image_url"),
                "is_active": item["is_active"],
                "children": [],
            }
            nodes[item["id"]] = node

        for item in items:
            node = nodes[item["id"]]
            parent_id = item["parent_id"]
            if parent_id is not None and parent_id in nodes:
                nodes[parent_id]["children"].append(node)
            else:
                roots.append(node)

        return roots

    @expose("/tree", methods=["GET"])
    async def category_tree(self, request: Request):
        async def _load(session):
            repository = CategoryRepository(session)
            categories = await repository.get_all_categories(include_inactive=True)
            return [
                {
                    "id": category.id,
                    "name": category.name,
                    "parent_id": category.parent_id,
                    "type": category.type.value,
                    "image_url": category.image_url,
                    "is_active": category.is_active,
                }
                for category in categories
            ]

        items = await with_image_session(_load)
        tree = self._build_tree_payload(items)
        return JSONResponse({"items": tree})

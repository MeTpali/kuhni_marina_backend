from sqladmin import ModelView

from core.models.categories import Category, CategoryType


class CategoryAdmin(ModelView, model=Category):
    name = "Категория"
    name_plural = "Категории"
    icon = "fa-solid fa-folder"
    column_list = [Category.id, Category.name, Category.slug, Category.type, Category.parent_id, Category.is_active, Category.created_at]
    column_details_list = [Category.id, Category.name, Category.slug, Category.type, Category.parent_id, Category.is_active, Category.created_at]
    column_searchable_list = [Category.name, Category.slug]
    column_sortable_list = [Category.id, Category.name, Category.created_at]
    column_labels = {
        Category.id: "ID",
        Category.name: "Название",
        Category.slug: "Slug",
        Category.type: "Тип",
        Category.parent_id: "Родительская категория",
        Category.is_active: "Активна",
        Category.created_at: "Дата создания",
    }
    form_columns = [Category.name, Category.slug, Category.type, Category.parent, Category.is_active]
    form_ajax_refs = {
        "parent": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }
    form_args = {
        "type": {
            "choices": [(cat_type.value, cat_type.name) for cat_type in CategoryType],
        }
    }

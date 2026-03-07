from sqladmin import ModelView

from core.models.discounts import Discount, DiscountType, DiscountScope
from core.models.products import ProductType


class DiscountAdmin(ModelView, model=Discount):
    name = "Скидка"
    name_plural = "Скидки"
    icon = "fa-solid fa-percent"
    column_list = [Discount.id, Discount.name, Discount.discount_type, Discount.value, Discount.scope, Discount.is_active, Discount.start_date, Discount.end_date, Discount.priority]
    column_details_list = [Discount.id, Discount.name, Discount.discount_type, Discount.value, Discount.scope, Discount.product_id, Discount.category_id, Discount.product_type, Discount.start_date, Discount.end_date, Discount.is_active, Discount.priority, Discount.created_at, Discount.updated_at]
    column_searchable_list = [Discount.name]
    column_sortable_list = [Discount.id, Discount.name, Discount.priority, Discount.start_date, Discount.end_date, Discount.created_at]
    column_labels = {
        Discount.id: "ID",
        Discount.name: "Название",
        Discount.discount_type: "Тип скидки",
        Discount.value: "Значение",
        Discount.scope: "Область применения",
        Discount.product_id: "Продукт",
        Discount.category_id: "Категория",
        Discount.product_type: "Тип продукта",
        Discount.start_date: "Дата начала",
        Discount.end_date: "Дата окончания",
        Discount.is_active: "Активна",
        Discount.priority: "Приоритет",
        Discount.created_at: "Дата создания",
        Discount.updated_at: "Дата обновления",
    }
    form_columns = [Discount.name, Discount.discount_type, Discount.value, Discount.scope, Discount.product, Discount.category, Discount.product_type, Discount.start_date, Discount.end_date, Discount.is_active, Discount.priority]
    form_ajax_refs = {
        "product": {
            "fields": ("name", "id"),
            "order_by": "name",
        },
        "category": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }
    form_args = {
        "discount_type": {
            "choices": [(disc_type.value, disc_type.name) for disc_type in DiscountType],
        },
        "scope": {
            "choices": [(scope.value, scope.name) for scope in DiscountScope],
        },
        "product_type": {
            "choices": [(prod_type.value, prod_type.name) for prod_type in ProductType],
        }
    }

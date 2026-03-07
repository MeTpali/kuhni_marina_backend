from sqladmin import ModelView

from core.models.product_attributes import ProductAttribute


class ProductAttributeAdmin(ModelView, model=ProductAttribute):
    name = "Атрибут продукта"
    name_plural = "Атрибуты продуктов"
    icon = "fa-solid fa-list"
    column_list = [ProductAttribute.product_id, ProductAttribute.attribute_id, ProductAttribute.value]
    column_details_list = [ProductAttribute.product_id, ProductAttribute.attribute_id, ProductAttribute.value]
    column_searchable_list = [ProductAttribute.value]
    column_sortable_list = [ProductAttribute.product_id, ProductAttribute.attribute_id]
    column_labels = {
        ProductAttribute.product_id: "Продукт",
        ProductAttribute.attribute_id: "Атрибут",
        ProductAttribute.value: "Значение",
    }
    form_columns = [ProductAttribute.product, ProductAttribute.attribute, ProductAttribute.value]
    form_ajax_refs = {
        "product": {
            "fields": ("name", "id"),
            "order_by": "name",
        },
        "attribute": {
            "fields": ("name", "id"),
            "order_by": "name",
        }
    }

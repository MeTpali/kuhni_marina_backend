from sqladmin import ModelView

from core.models.attributes import Attribute


class AttributeAdmin(ModelView, model=Attribute):
    name = "Атрибут"
    name_plural = "Атрибуты"
    icon = "fa-solid fa-tag"
    column_list = [Attribute.id, Attribute.name, Attribute.unit]
    column_details_list = [Attribute.id, Attribute.name, Attribute.unit]
    column_searchable_list = [Attribute.name]
    column_sortable_list = [Attribute.id, Attribute.name]
    column_labels = {
        Attribute.id: "ID",
        Attribute.name: "Название",
        Attribute.unit: "Единица измерения",
    }
    form_columns = [Attribute.name, Attribute.unit]

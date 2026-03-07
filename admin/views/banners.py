from sqladmin import ModelView

from core.models.banners import Banner


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

from sqladmin import ModelView

from core.models.reviews import Review


class ReviewAdmin(ModelView, model=Review):
    name = "Отзыв"
    name_plural = "Отзывы"
    icon = "fa-solid fa-star"
    column_list = [Review.id, Review.author_name, Review.rating, Review.product_id, Review.is_approved, Review.created_at]
    column_details_list = [Review.id, Review.author_name, Review.rating, Review.text, Review.product_id, Review.is_approved, Review.created_at]
    column_searchable_list = [Review.author_name, Review.text]
    column_sortable_list = [Review.id, Review.rating, Review.created_at]
    column_labels = {
        Review.id: "ID",
        Review.author_name: "Имя автора",
        Review.rating: "Оценка",
        Review.text: "Текст",
        Review.product_id: "Продукт",
        Review.is_approved: "Одобрен",
        Review.created_at: "Дата создания",
    }
    form_columns = [Review.author_name, Review.rating, Review.text, Review.product, Review.is_approved]
    form_ajax_refs = {
        "product": {
            "fields": ("name", "id"),
            "order_by": "name",
        },
        "user": {
            "fields": ("full_name", "id"),
            "order_by": "full_name",
        }
    }

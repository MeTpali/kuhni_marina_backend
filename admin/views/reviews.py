from sqladmin import ModelView
from sqladmin.filters import StaticValuesFilter

from core.models.reviews import Review, ReviewStatus

REVIEW_STATUS_LABELS = {"PENDING": "Ожидает", "APPROVED": "Одобрен", "DECLINED": "Отклонён"}
REVIEW_STATUS_CHOICES = [(s.value, REVIEW_STATUS_LABELS.get(s.value, s.value)) for s in ReviewStatus]


class ReviewAdmin(ModelView, model=Review):
    name = "Отзыв"
    name_plural = "Отзывы"
    icon = "fa-solid fa-star"
    column_list = [Review.id, Review.author_name, Review.rating, Review.product_id, Review.status, Review.created_at]
    column_details_list = [Review.id, Review.author_name, Review.rating, Review.text, Review.product_id, Review.status, Review.created_at]
    column_searchable_list = [Review.author_name, Review.text]
    column_sortable_list = [Review.id, Review.rating, Review.created_at]
    column_filters = [
        StaticValuesFilter(Review.status, REVIEW_STATUS_CHOICES, title="Статус"),
    ]
    column_labels = {
        Review.id: "ID",
        Review.author_name: "Имя автора",
        Review.rating: "Оценка",
        Review.text: "Текст",
        Review.product_id: "Продукт",
        Review.status: "Статус",
        Review.created_at: "Дата создания",
    }
    form_columns = [Review.author_name, Review.rating, Review.text, Review.product, Review.status]
    form_args = {
        "status": {
            "choices": REVIEW_STATUS_CHOICES,
        }
    }
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

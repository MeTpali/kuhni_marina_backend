from sqladmin import ModelView
from sqladmin.filters import StaticValuesFilter

from core.models.measure_requests import MeasureRequest, MeasureRequestStatus

MEASURE_REQUEST_STATUS_LABELS = {"NEW": "Новая", "IN_PROGRESS": "В работе", "DONE": "Выполнена", "CANCELLED": "Отменена"}
MEASURE_REQUEST_STATUS_CHOICES = [(s.value, MEASURE_REQUEST_STATUS_LABELS.get(s.value, s.value)) for s in MeasureRequestStatus]


class MeasureRequestAdmin(ModelView, model=MeasureRequest):
    name = "Заявка на замер"
    name_plural = "Заявки на замер"
    icon = "fa-solid fa-ruler"
    column_list = [MeasureRequest.id, MeasureRequest.full_name, MeasureRequest.phone, MeasureRequest.status, MeasureRequest.created_at]
    column_details_list = [MeasureRequest.id, MeasureRequest.full_name, MeasureRequest.phone, MeasureRequest.address, MeasureRequest.preferred_date, MeasureRequest.comment, MeasureRequest.status, MeasureRequest.created_at]
    column_searchable_list = [MeasureRequest.full_name, MeasureRequest.phone, MeasureRequest.address]
    column_sortable_list = [MeasureRequest.id, MeasureRequest.status, MeasureRequest.created_at]
    column_filters = [
        StaticValuesFilter(MeasureRequest.status, MEASURE_REQUEST_STATUS_CHOICES, title="Статус"),
    ]
    column_labels = {
        MeasureRequest.id: "ID",
        MeasureRequest.full_name: "Имя клиента",
        MeasureRequest.phone: "Телефон",
        MeasureRequest.address: "Адрес",
        MeasureRequest.preferred_date: "Предпочтительная дата",
        MeasureRequest.comment: "Комментарий",
        MeasureRequest.status: "Статус",
        MeasureRequest.created_at: "Дата создания",
    }
    form_columns = [MeasureRequest.full_name, MeasureRequest.phone, MeasureRequest.address, MeasureRequest.preferred_date, MeasureRequest.comment, MeasureRequest.status]
    form_args = {
        "status": {
            "choices": MEASURE_REQUEST_STATUS_CHOICES,
        }
    }

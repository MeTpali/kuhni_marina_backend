from sqladmin import ModelView

from core.models.measure_requests import MeasureRequest, MeasureRequestStatus


class MeasureRequestAdmin(ModelView, model=MeasureRequest):
    name = "Заявка на замер"
    name_plural = "Заявки на замер"
    icon = "fa-solid fa-ruler"
    column_list = [MeasureRequest.id, MeasureRequest.full_name, MeasureRequest.phone, MeasureRequest.status, MeasureRequest.created_at]
    column_details_list = [MeasureRequest.id, MeasureRequest.full_name, MeasureRequest.phone, MeasureRequest.address, MeasureRequest.preferred_date, MeasureRequest.comment, MeasureRequest.status, MeasureRequest.created_at]
    column_searchable_list = [MeasureRequest.full_name, MeasureRequest.phone, MeasureRequest.address]
    column_sortable_list = [MeasureRequest.id, MeasureRequest.status, MeasureRequest.created_at]
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
            "choices": [(status.value, status.name) for status in MeasureRequestStatus],
        }
    }

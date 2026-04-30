import asyncio
from urllib.parse import quote

from fastapi import Request
from sqladmin import BaseView, ModelView, expose
from sqladmin.fields import FileField
from starlette.responses import HTMLResponse, RedirectResponse

from admin.bulk_assets import BULK_IMAGES_CSS
from admin.helpers import with_image_session
from core.models.background_images import BackgroundImage
from core.storage import upload_background_image


def _is_upload_file(obj) -> bool:
    return obj is not None and hasattr(obj, "read") and getattr(obj, "filename", None)


async def _background_image_url_from_file(data: dict) -> None:
    f = data.pop("image_file", None)
    if not _is_upload_file(f):
        return
    body = await f.read()
    content_type = getattr(f, "content_type", None) or ""
    filename = getattr(f, "filename", None)
    url = await asyncio.to_thread(
        upload_background_image,
        body,
        content_type or None,
        filename,
    )
    data["url"] = url


class BackgroundImageAdmin(ModelView, model=BackgroundImage):
    name = "Фоновое изображение"
    name_plural = "Фоновые изображения"
    icon = "fa-solid fa-image"
    column_list = [BackgroundImage.id, BackgroundImage.url, BackgroundImage.is_active]
    column_details_list = [BackgroundImage.id, BackgroundImage.url, BackgroundImage.is_active]
    column_searchable_list = [BackgroundImage.url]
    column_sortable_list = [BackgroundImage.id]
    column_labels = {
        BackgroundImage.id: "ID",
        BackgroundImage.url: "URL",
        BackgroundImage.is_active: "Активно",
    }
    form_columns = [BackgroundImage.is_active]

    async def scaffold_form(self, rules=None):
        form_class = await super().scaffold_form(rules)

        class FormWithFile(form_class):
            image_file = FileField("Фоновое изображение (файл)")

        return FormWithFile

    async def insert_model(self, request: Request, data: dict) -> BackgroundImage:
        await _background_image_url_from_file(data)
        if not (data.get("url") or "").strip():
            raise ValueError("Загрузите файл изображения.")
        return await super().insert_model(request, data)

    async def update_model(self, request: Request, pk: str, data: dict) -> BackgroundImage:
        await _background_image_url_from_file(data)
        if not (data.get("url") or "").strip():
            async def _load_current_url(session):
                model = await session.get(BackgroundImage, int(pk))
                if model and model.url:
                    data["url"] = model.url

            await with_image_session(_load_current_url)
        return await super().update_model(request, pk, data)


class BulkBackgroundImagesAdmin(BaseView):
    name = "Добавить несколько фоновых изображений"
    icon = "fa-solid fa-images"

    @expose("/bulk-background-images", methods=["GET", "POST"])
    async def bulk_background_images(self, request: Request):
        base_path = "/admin/bulk-background-images"
        if request.method == "POST":
            form = await request.form()
            files = form.getlist("images") if hasattr(form, "getlist") else []
            is_active_raw = (form.get("is_active") or "").lower()
            is_active = is_active_raw in {"1", "true", "on", "yes"}
            if not files:
                return RedirectResponse(base_path + "?error=Выберите+хотя+бы+один+файл", status_code=303)

            image_urls = []
            for f in files:
                if getattr(f, "filename", None) is None or not getattr(f, "read", None):
                    continue
                try:
                    data = await f.read()
                    content_type = getattr(f, "content_type", None) or ""
                    filename = getattr(f, "filename", None)
                    url = await asyncio.to_thread(
                        upload_background_image,
                        data,
                        content_type or None,
                        filename,
                    )
                    image_urls.append(url)
                except ValueError as e:
                    return RedirectResponse(base_path + "?error=" + quote(str(e)), status_code=303)

            if not image_urls:
                return RedirectResponse(base_path + "?error=Нет+допустимых+изображений", status_code=303)

            async def _add(session):
                created = []
                for image_url in image_urls:
                    item = BackgroundImage(url=image_url, is_active=is_active)
                    session.add(item)
                    created.append(item)
                await session.commit()
                return created

            created = await with_image_session(_add)
            return RedirectResponse(
                base_path + "?success=" + quote(f"Добавлено изображений: {len(created)}"),
                status_code=303,
            )

        error = request.query_params.get("error", "")
        success = request.query_params.get("success", "")
        error_html = f'<div class="bulk-alert bulk-alert-error">{error}</div>' if error else ""
        success_html = f'<div class="bulk-alert bulk-alert-success">{success}</div>' if success else ""
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Массовое добавление фоновых изображений</title>
  <style>{BULK_IMAGES_CSS}</style>
</head>
<body class="bulk-page">
  <div class="bulk-container">
    <div class="bulk-card">
      <h1 class="bulk-title">Массовое добавление фоновых изображений</h1>
      <p class="bulk-subtitle">Каждый загруженный файл будет создан как отдельная запись фонового изображения.</p>
      {error_html}
      {success_html}
      <form method="post" action="" enctype="multipart/form-data">
        <div class="bulk-form-group">
          <label for="images">Файлы изображений</label>
          <input type="file" id="images" name="images" class="bulk-file-input" accept="image/jpeg,image/png,image/gif,image/webp" multiple required>
          <p class="bulk-hint">JPEG, PNG, GIF или WebP. Максимум 10 МБ на файл.</p>
        </div>
        <div class="bulk-form-group">
          <label>
            <input type="checkbox" name="is_active" checked>
            Сделать добавленные изображения активными
          </label>
        </div>
        <button type="submit" class="bulk-btn">Загрузить и сохранить</button>
      </form>
    </div>
    <a href="/admin/" class="bulk-back">← Назад в админку</a>
  </div>
</body>
</html>"""
        return HTMLResponse(html)

    def is_visible(self, request: Request) -> bool:
        return True

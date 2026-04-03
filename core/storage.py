"""
Загрузка файлов в Yandex Cloud Object Storage (S3-совместимый API).
Структура бакета: products/{product_id}/{filename}, projects/{project_id}/{filename},
banners/, campaigns/, categories/ для общих изображений.
"""
import logging
import uuid
from typing import Optional

import boto3
from botocore.config import Config

from core.config import settings

logger = logging.getLogger(__name__)

# Публичный URL без пути к бакету (storage.yandexcloud.net/{bucket}/...)
YC_ENDPOINT = "https://storage.yandexcloud.net"

# Допустимые MIME-типы изображений
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}

# Максимальный размер файла (10 МБ)
MAX_FILE_SIZE = 10 * 1024 * 1024


def _get_client():
    return boto3.client(
        "s3",
        endpoint_url=YC_ENDPOINT,
        region_name="ru-central1",
        aws_access_key_id=settings.YC_UPLOADER_ID,
        aws_secret_access_key=settings.YC_UPLOADER_KEY,
        config=Config(signature_version="s3v4"),
    )


def _extension_from_content_type(content_type: Optional[str]) -> str:
    if not content_type:
        return "jpg"
    ct = content_type.lower().split(";")[0].strip()
    mime_to_ext = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "image/webp": "webp",
    }
    return mime_to_ext.get(ct, "jpg")


def _extension_from_filename(filename: Optional[str]) -> Optional[str]:
    if not filename or "." not in filename:
        return None
    return filename.rsplit(".", 1)[-1].lower()


def upload_product_image(
    product_id: int,
    file_bytes: bytes,
    content_type: Optional[str] = None,
    original_filename: Optional[str] = None,
) -> str:
    """
    Загружает изображение продукта в бакет: products/{product_id}/{uuid}.{ext}.
    Возвращает публичный URL файла.
    """
    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError(f"Размер файла не должен превышать {MAX_FILE_SIZE // (1024*1024)} МБ")
    if content_type and content_type.split(";")[0].strip().lower() not in ALLOWED_IMAGE_TYPES:
        raise ValueError(f"Допустимые типы: {', '.join(ALLOWED_IMAGE_TYPES)}")

    ext = _extension_from_filename(original_filename) or _extension_from_content_type(content_type)
    safe_ext = ext if ext in ("jpg", "jpeg", "png", "gif", "webp") else "jpg"
    key = f"products/{product_id}/{uuid.uuid4().hex}.{safe_ext}"

    client = _get_client()
    client.put_object(
        Bucket=settings.YC_STORAGE,
        Key=key,
        Body=file_bytes,
        ContentType=content_type or "image/jpeg",
    )
    url = f"{YC_ENDPOINT}/{settings.YC_STORAGE}/{key}"
    logger.info("Uploaded product image to %s", url)
    return url


def upload_project_image(
    project_id: int,
    file_bytes: bytes,
    content_type: Optional[str] = None,
    original_filename: Optional[str] = None,
) -> str:
    """
    Загружает изображение проекта в бакет: projects/{project_id}/{uuid}.{ext}.
    Возвращает публичный URL файла.
    """
    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError(f"Размер файла не должен превышать {MAX_FILE_SIZE // (1024*1024)} МБ")
    if content_type and content_type.split(";")[0].strip().lower() not in ALLOWED_IMAGE_TYPES:
        raise ValueError(f"Допустимые типы: {', '.join(ALLOWED_IMAGE_TYPES)}")

    ext = _extension_from_filename(original_filename) or _extension_from_content_type(content_type)
    safe_ext = ext if ext in ("jpg", "jpeg", "png", "gif", "webp") else "jpg"
    key = f"projects/{project_id}/{uuid.uuid4().hex}.{safe_ext}"

    client = _get_client()
    client.put_object(
        Bucket=settings.YC_STORAGE,
        Key=key,
        Body=file_bytes,
        ContentType=content_type or "image/jpeg",
    )
    url = f"{YC_ENDPOINT}/{settings.YC_STORAGE}/{key}"
    logger.info("Uploaded project image to %s", url)
    return url


def _upload_image_to_folder(
    folder: str,
    file_bytes: bytes,
    content_type: Optional[str] = None,
    original_filename: Optional[str] = None,
) -> str:
    """Загружает изображение в бакет в папку folder/{uuid}.{ext}. Возвращает публичный URL."""
    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError(f"Размер файла не должен превышать {MAX_FILE_SIZE // (1024*1024)} МБ")
    if content_type and content_type.split(";")[0].strip().lower() not in ALLOWED_IMAGE_TYPES:
        raise ValueError(f"Допустимые типы: {', '.join(ALLOWED_IMAGE_TYPES)}")

    ext = _extension_from_filename(original_filename) or _extension_from_content_type(content_type)
    safe_ext = ext if ext in ("jpg", "jpeg", "png", "gif", "webp") else "jpg"
    key = f"{folder}/{uuid.uuid4().hex}.{safe_ext}"

    client = _get_client()
    client.put_object(
        Bucket=settings.YC_STORAGE,
        Key=key,
        Body=file_bytes,
        ContentType=content_type or "image/jpeg",
    )
    url = f"{YC_ENDPOINT}/{settings.YC_STORAGE}/{key}"
    logger.info("Uploaded image to %s", url)
    return url


def upload_banner_image(
    file_bytes: bytes,
    content_type: Optional[str] = None,
    original_filename: Optional[str] = None,
) -> str:
    """Загружает изображение баннера в бакет: banners/{uuid}.{ext}. Возвращает публичный URL."""
    return _upload_image_to_folder("banners", file_bytes, content_type, original_filename)


def upload_campaign_image(
    file_bytes: bytes,
    content_type: Optional[str] = None,
    original_filename: Optional[str] = None,
) -> str:
    """Загружает изображение акции в бакет: campaigns/{uuid}.{ext}. Возвращает публичный URL."""
    return _upload_image_to_folder("campaigns", file_bytes, content_type, original_filename)


def upload_category_image(
    file_bytes: bytes,
    content_type: Optional[str] = None,
    original_filename: Optional[str] = None,
) -> str:
    """Загружает изображение категории в бакет: categories/{uuid}.{ext}. Возвращает публичный URL."""
    return _upload_image_to_folder("categories", file_bytes, content_type, original_filename)

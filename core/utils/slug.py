from typing import Optional, Type
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from slugify import slugify as slugify_func


async def generate_unique_slug(
    session: AsyncSession,
    model: Type[DeclarativeBase],
    text: str,
    exclude_id: Optional[int] = None,
    max_length: int = 255,
) -> str:
    """
    Генерирует уникальный slug из текста для указанной модели.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        model: Модель SQLAlchemy, у которой есть поле slug
        text: Исходный текст для генерации slug
        exclude_id: ID записи, которую нужно исключить из проверки (для обновления)
        max_length: Максимальная длина slug
        
    Returns:
        Уникальный slug
    """
    # Генерируем базовый slug из текста
    # python-slugify поддерживает max_length и word_boundary
    # max_length=0 означает без ограничения, поэтому используем наше значение
    base_slug = slugify_func(
        text,
        lowercase=True,
        separator='-',
        max_length=max_length if max_length > 0 else 0,
        word_boundary=True
    )
    
    if not base_slug:
        # Если slug пустой, используем дефолтное значение
        base_slug = "item"
    
    # Проверяем уникальность
    slug = base_slug
    counter = 1
    
    while True:
        # Формируем запрос для проверки существования slug
        query = select(model).where(model.slug == slug)
        
        # Исключаем текущую запись при обновлении
        if exclude_id is not None:
            query = query.where(model.id != exclude_id)
        
        result = await session.execute(query)
        existing = result.scalar_one_or_none()
        
        # Если slug уникален, возвращаем его
        if existing is None:
            return slug
        
        # Если slug уже существует, добавляем суффикс
        # Обрезаем базовый slug, чтобы оставить место для суффикса
        suffix = f"-{counter}"
        available_length = max_length - len(suffix)
        truncated_base = base_slug[:available_length] if len(base_slug) > available_length else base_slug
        slug = f"{truncated_base}{suffix}"
        counter += 1
        
        # Защита от бесконечного цикла (на практике не должно произойти)
        if counter > 10000:
            raise ValueError(f"Не удалось сгенерировать уникальный slug для '{text}' после 10000 попыток")

from fastapi import APIRouter, Depends, status

from api.deps import get_review_service
from services.reviews import ReviewService
from core.schemas.reviews import (
    ReviewCreateRequest,
    ReviewUpdateRequest,
    ReviewResponse,
    ReviewListResponse,
    ReviewDeleteResponse,
)

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    responses={404: {"description": "Review not found"}},
)


@router.get(
    "",
    response_model=ReviewListResponse,
    summary="Получить все отзывы",
    description="Возвращает список всех отзывов",
)
async def get_reviews(
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Получить список всех отзывов:
    - Возвращает все существующие отзывы
    - Отсортированы по дате создания (новые сначала)
    """
    return await review_service.get_all_reviews()


@router.get(
    "/product/{product_id}",
    response_model=ReviewListResponse,
    summary="Получить отзывы по идентификатору продукта",
    description="Возвращает список отзывов для указанного продукта",
    responses={
        200: {"description": "Отзывы найдены"},
    },
)
async def get_reviews_by_product_id(
    product_id: int,
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Получить список отзывов по идентификатору продукта:
    - Возвращает все отзывы для указанного продукта
    - Отсортированы по дате создания (новые сначала)
    """
    return await review_service.get_reviews_by_product_id(product_id)


@router.get(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Получить отзыв по идентификатору",
    description="Возвращает отзыв с указанным идентификатором",
    responses={
        200: {"description": "Отзыв найден"},
        404: {"description": "Отзыв не найден"},
    },
)
async def get_review_by_id(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Получить отзыв по идентификатору:
    - Возвращает отзыв, если он существует
    - Возвращает ошибку 404, если отзыв не найден
    """
    return await review_service.get_review_by_id(review_id)


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать отзыв",
    description="Создает и возвращает новый отзыв",
    responses={
        201: {"description": "Отзыв успешно создан"},
        400: {"description": "Некорректные данные для отзыва"},
    },
)
async def create_review(
    request: ReviewCreateRequest,
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Создать новый отзыв:
    - Проверяет корректность данных
    - Оценка должна быть от 1 до 5
    - По умолчанию отзыв имеет статус pending (ожидает модерации)
    - Создает и возвращает созданный отзыв
    """
    return await review_service.create_review(request)


@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Обновить отзыв",
    description="Обновляет отзыв по идентификатору",
    responses={
        200: {"description": "Отзыв успешно обновлен"},
        400: {"description": "Некорректные данные для отзыва"},
        404: {"description": "Отзыв не найден"},
    },
)
async def update_review(
    review_id: int,
    request: ReviewUpdateRequest,
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Обновить отзыв:
    - Проверяет корректность данных
    - Обновляет указанные поля отзыва
    - Поля, которые не указаны, остаются без изменений
    """
    return await review_service.update_review(review_id, request)


@router.patch(
    "/{review_id}/approve",
    response_model=ReviewResponse,
    summary="Одобрить отзыв",
    description="Одобряет отзыв по идентификатору",
    responses={
        200: {"description": "Отзыв успешно одобрен"},
        404: {"description": "Отзыв не найден"},
    },
)
async def approve_review(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Одобрить отзыв:
    - Устанавливает статус approved для отзыва
    - Используется для модерации отзывов
    """
    return await review_service.approve_review(review_id)


@router.delete(
    "/{review_id}",
    response_model=ReviewDeleteResponse,
    summary="Удалить отзыв",
    description="Удаляет отзыв по идентификатору",
    responses={
        200: {"description": "Отзыв успешно удален"},
        404: {"description": "Отзыв не найден"},
    },
)
async def delete_review(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Удалить отзыв:
    - Удаляет отзыв по идентификатору
    - Каскадное удаление связанных сущностей настроено в БД
    """
    return await review_service.delete_review(review_id)


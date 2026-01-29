import logging

from fastapi import HTTPException, status

from repositories.reviews import ReviewRepository
from core.schemas.reviews import (
    ReviewCreateRequest,
    ReviewUpdateRequest,
    ReviewResponse,
    ReviewListResponse,
    ReviewDeleteResponse,
)

logger = logging.getLogger(__name__)


class ReviewService:
    def __init__(self, repository: ReviewRepository):
        self.repository = repository

    async def get_all_reviews(self) -> ReviewListResponse:
        """
        Получить список всех отзывов.
        """
        logger.info("Fetching all reviews via service")
        reviews = await self.repository.get_all_reviews()
        items = [
            ReviewResponse(
                id=review.id,
                product_id=review.product_id,
                user_id=review.user_id,
                author_name=review.author_name,
                rating=review.rating,
                text=review.text,
                created_at=review.created_at,
                is_approved=review.is_approved,
                message=None,
            )
            for review in reviews
        ]

        response = ReviewListResponse(
            items=items,
            message="Список отзывов успешно получен",
        )
        logger.info("Successfully fetched %d reviews", len(items))
        return response

    async def get_reviews_by_product_id(self, product_id: int) -> ReviewListResponse:
        """
        Получить список отзывов по идентификатору продукта.
        """
        logger.info("Fetching reviews by product_id: %s via service", product_id)
        reviews = await self.repository.get_reviews_by_product_id(product_id)
        items = [
            ReviewResponse(
                id=review.id,
                product_id=review.product_id,
                user_id=review.user_id,
                author_name=review.author_name,
                rating=review.rating,
                text=review.text,
                created_at=review.created_at,
                is_approved=review.is_approved,
                message=None,
            )
            for review in reviews
        ]

        response = ReviewListResponse(
            items=items,
            message=f"Список отзывов для продукта с id {product_id} успешно получен",
        )
        logger.info("Successfully fetched %d reviews for product_id %s", len(items), product_id)
        return response

    async def get_review_by_id(self, review_id: int) -> ReviewResponse:
        """
        Получить отзыв по идентификатору.
        """
        logger.info("Fetching review by id: %s via service", review_id)
        review = await self.repository.get_review_by_id(review_id)
        if not review:
            logger.error("Review with id %s not found", review_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Отзыв с id {review_id} не найден",
            )

        response = ReviewResponse(
            id=review.id,
            product_id=review.product_id,
            user_id=review.user_id,
            author_name=review.author_name,
            rating=review.rating,
            text=review.text,
            created_at=review.created_at,
            is_approved=review.is_approved,
            message="Отзыв успешно найден",
        )
        logger.info("Review with id %s successfully retrieved", review_id)
        return response

    async def create_review(
        self,
        request: ReviewCreateRequest,
    ) -> ReviewResponse:
        """
        Создать новый отзыв.
        """
        logger.info("Creating review via service by author '%s'", request.author_name)

        if len(request.author_name.strip()) < 2:
            logger.error("Review author_name too short: '%s'", request.author_name)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя автора должно содержать минимум 2 символа",
            )

        if request.rating < 1 or request.rating > 5:
            logger.error("Review rating out of range: %s", request.rating)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Оценка должна быть от 1 до 5",
            )

        if len(request.text.strip()) < 5:
            logger.error("Review text too short")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Текст отзыва должен содержать минимум 5 символов",
            )

        review = await self.repository.create_review(request)

        response = ReviewResponse(
            id=review.id,
            product_id=review.product_id,
            user_id=review.user_id,
            author_name=review.author_name,
            rating=review.rating,
            text=review.text,
            created_at=review.created_at,
            is_approved=review.is_approved,
            message="Отзыв успешно создан",
        )
        logger.info("Review created with id %s via service", review.id)
        return response

    async def update_review(
        self,
        review_id: int,
        request: ReviewUpdateRequest,
    ) -> ReviewResponse:
        """
        Обновить отзыв по идентификатору.
        """
        logger.info("Updating review via service with id %s", review_id)

        if request.author_name is not None and len(request.author_name.strip()) < 2:
            logger.error("Review author_name too short: '%s'", request.author_name)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя автора должно содержать минимум 2 символа",
            )

        if request.rating is not None and (request.rating < 1 or request.rating > 5):
            logger.error("Review rating out of range: %s", request.rating)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Оценка должна быть от 1 до 5",
            )

        if request.text is not None and len(request.text.strip()) < 5:
            logger.error("Review text too short")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Текст отзыва должен содержать минимум 5 символов",
            )

        review = await self.repository.update_review(review_id, request)
        if not review:
            logger.error("Review with id %s not found for update", review_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Отзыв с id {review_id} не найден",
            )

        response = ReviewResponse(
            id=review.id,
            product_id=review.product_id,
            user_id=review.user_id,
            author_name=review.author_name,
            rating=review.rating,
            text=review.text,
            created_at=review.created_at,
            is_approved=review.is_approved,
            message="Отзыв успешно обновлен",
        )
        logger.info("Review with id %s successfully updated via service", review_id)
        return response

    async def approve_review(self, review_id: int) -> ReviewResponse:
        """
        Одобрить отзыв по идентификатору.
        """
        logger.info("Approving review via service with id %s", review_id)
        review = await self.repository.approve_review(review_id)
        if not review:
            logger.error("Review with id %s not found for approval", review_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Отзыв с id {review_id} не найден",
            )

        response = ReviewResponse(
            id=review.id,
            product_id=review.product_id,
            user_id=review.user_id,
            author_name=review.author_name,
            rating=review.rating,
            text=review.text,
            created_at=review.created_at,
            is_approved=review.is_approved,
            message="Отзыв успешно одобрен",
        )
        logger.info("Review with id %s successfully approved via service", review_id)
        return response

    async def delete_review(self, review_id: int) -> ReviewDeleteResponse:
        """
        Удалить отзыв по идентификатору.
        """
        logger.info("Deleting review via service with id %s", review_id)
        success = await self.repository.delete_review(review_id)
        if not success:
            logger.error("Review with id %s not found for deletion", review_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Отзыв с id {review_id} не найден",
            )

        response = ReviewDeleteResponse(
            review_id=review_id,
            message="Отзыв успешно удален",
        )
        logger.info("Review with id %s successfully deleted via service", review_id)
        return response


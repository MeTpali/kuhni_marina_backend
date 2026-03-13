from typing import List, Optional
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.reviews import Review, ReviewStatus
from core.schemas.reviews import ReviewCreateRequest, ReviewUpdateRequest

logger = logging.getLogger(__name__)


class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_reviews(self) -> List[Review]:
        """
        Получить список всех отзывов.
        """
        logger.info("Fetching all reviews")
        query = select(Review).order_by(Review.created_at.desc(), Review.id)
        result = await self.session.execute(query)
        reviews = result.scalars().all()
        logger.info("Retrieved %d reviews", len(reviews))
        return reviews

    async def get_reviews_by_product_id(self, product_id: int) -> List[Review]:
        """
        Получить список отзывов по идентификатору продукта.
        """
        logger.info("Fetching reviews for product_id %s", product_id)
        query = select(Review).where(Review.product_id == product_id).order_by(Review.created_at.desc(), Review.id)
        result = await self.session.execute(query)
        reviews = result.scalars().all()
        logger.info("Retrieved %d reviews for product_id %s", len(reviews), product_id)
        return reviews

    async def get_review_by_id(self, review_id: int) -> Optional[Review]:
        """
        Получить отзыв по идентификатору.
        """
        logger.info("Fetching review with id %s", review_id)
        query = select(Review).where(Review.id == review_id)
        result = await self.session.execute(query)
        review = result.scalar_one_or_none()

        if review is None:
            logger.warning("Review with id %s not found", review_id)
        return review

    async def create_review(self, request: ReviewCreateRequest) -> Review:
        """
        Создать новый отзыв.
        """
        logger.info("Creating review for product_id %s by author '%s'", request.product_id, request.author_name)
        review = Review(
            product_id=request.product_id,
            user_id=request.user_id,
            author_name=request.author_name,
            rating=request.rating,
            text=request.text,
            status=request.status or ReviewStatus.PENDING,
        )

        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)

        logger.info("Review created with id %s", review.id)
        return review

    async def update_review(
        self, review_id: int, request: ReviewUpdateRequest
    ) -> Optional[Review]:
        """
        Обновить отзыв по идентификатору.
        """
        logger.info("Updating review with id %s", review_id)
        review = await self.get_review_by_id(review_id)
        if review is None:
            logger.warning("Review with id %s not found for update", review_id)
            return None

        if request.author_name is not None:
            review.author_name = request.author_name
        if request.rating is not None:
            review.rating = request.rating
        if request.text is not None:
            review.text = request.text
        if request.product_id is not None:
            review.product_id = request.product_id
        if request.user_id is not None:
            review.user_id = request.user_id
        if request.status is not None:
            review.status = request.status

        await self.session.commit()
        await self.session.refresh(review)

        logger.info("Review with id %s successfully updated", review_id)
        return review

    async def approve_review(self, review_id: int) -> Optional[Review]:
        """
        Одобрить отзыв по идентификатору.
        """
        logger.info("Approving review with id %s", review_id)
        review = await self.get_review_by_id(review_id)
        if review is None:
            logger.warning("Review with id %s not found for approval", review_id)
            return None

        review.status = ReviewStatus.APPROVED
        await self.session.commit()
        await self.session.refresh(review)

        logger.info("Review with id %s successfully approved", review_id)
        return review

    async def delete_review(self, review_id: int) -> bool:
        """
        Удалить отзыв по идентификатору.
        """
        logger.info("Deleting review with id %s", review_id)
        review = await self.get_review_by_id(review_id)
        if review is None:
            logger.warning("Review with id %s not found for deletion", review_id)
            return False

        await self.session.delete(review)
        await self.session.commit()

        logger.info("Review with id %s successfully deleted", review_id)
        return True


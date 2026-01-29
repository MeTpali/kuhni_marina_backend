from typing import List, Optional
from datetime import datetime

from .base import BaseSchema


class ReviewBase(BaseSchema):
    author_name: str
    rating: int
    text: str
    product_id: Optional[int] = None
    user_id: Optional[int] = None
    is_approved: Optional[bool] = False


class ReviewCreateRequest(ReviewBase):
    pass


class ReviewUpdateRequest(BaseSchema):
    author_name: Optional[str] = None
    rating: Optional[int] = None
    text: Optional[str] = None
    product_id: Optional[int] = None
    user_id: Optional[int] = None


class ReviewResponse(ReviewBase):
    id: int
    created_at: datetime
    is_approved: bool
    message: Optional[str] = None


class ReviewListResponse(BaseSchema):
    items: List[ReviewResponse]
    message: Optional[str] = None


class ReviewDeleteResponse(BaseSchema):
    review_id: int
    message: Optional[str] = None


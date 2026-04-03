"""categories: add optional image_url

Revision ID: categories_image_url
Revises: banners_priority
Create Date: 2026-04-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "categories_image_url"
down_revision: Union[str, None] = "banners_priority"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("categories", sa.Column("image_url", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("categories", "image_url")

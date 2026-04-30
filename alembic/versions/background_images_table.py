"""create background_images table

Revision ID: background_images_table
Revises: categories_image_url
Create Date: 2026-04-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "background_images_table"
down_revision: Union[str, None] = "categories_image_url"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "background_images",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_background_images_id", "background_images", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_background_images_id", table_name="background_images")
    op.drop_table("background_images")

"""banners: position -> priority

Revision ID: banners_priority
Revises: 527b8c2bcc8c
Create Date: 2025-03-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "banners_priority"
down_revision: Union[str, None] = "527b8c2bcc8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "banners",
        "position",
        new_column_name="priority",
        existing_type=sa.Integer(),
        existing_nullable=False,
        existing_server_default=sa.text("0"),
    )
    # Переименовать индекс, если он есть (как в create_tables.sql)
    op.execute("DROP INDEX IF EXISTS idx_banners_position")
    op.create_index("idx_banners_priority", "banners", ["priority"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_banners_priority", table_name="banners")
    op.alter_column(
        "banners",
        "priority",
        new_column_name="position",
        existing_type=sa.Integer(),
        existing_nullable=False,
        existing_server_default=sa.text("0"),
    )
    op.create_index("idx_banners_position", "banners", ["position"], unique=False)

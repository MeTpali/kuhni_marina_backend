"""Create texts table

Revision ID: 001
Revises: 
Create Date: 2024-12-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create schema if it doesn't exist
    op.execute("CREATE SCHEMA IF NOT EXISTS hash_clash")
    
    # Create users table first (texts depends on it)
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('user_type', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('is_email_confirmed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('totp_key', sa.String(), nullable=True),
        sa.Column('is_totp_confirmed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        schema='hash_clash'
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False, schema='hash_clash')
    op.create_index('ix_users_username', 'users', ['username'], unique=True, schema='hash_clash')
    op.create_index('ix_users_email', 'users', ['email'], unique=True, schema='hash_clash')
    
    # Create texts table
    op.create_table('texts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('encryption_type', sa.String(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['hash_clash.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='hash_clash'
    )
    op.create_index(op.f('ix_texts_id'), 'texts', ['id'], unique=False, schema='hash_clash')


def downgrade() -> None:
    # Drop texts table
    op.drop_index(op.f('ix_texts_id'), table_name='texts', schema='hash_clash')
    op.drop_table('texts', schema='hash_clash')
    
    # Drop users table
    op.drop_index('ix_users_email', table_name='users', schema='hash_clash')
    op.drop_index('ix_users_username', table_name='users', schema='hash_clash')
    op.drop_index(op.f('ix_users_id'), table_name='users', schema='hash_clash')
    op.drop_table('users', schema='hash_clash')

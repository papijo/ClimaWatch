"""add unknown to facility enums and category column

Revision ID: a1b2c3d4e5f6
Revises: 897441522362
Create Date: 2026-06-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '897441522362'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE facility_type ADD VALUE IF NOT EXISTS 'unknown'")
    op.execute("ALTER TYPE facility_ownership ADD VALUE IF NOT EXISTS 'unknown'")
    op.add_column('health_facilities', sa.Column('category', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('health_facilities', 'category')
    # PostgreSQL does not support removing values from enums.
    # To fully reverse, recreate the enum types without 'unknown'.

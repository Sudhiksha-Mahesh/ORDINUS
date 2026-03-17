"""Add break_after_slot_1 and break_after_slot_2 to classes

Revision ID: 003
Revises: 002
Create Date: 2025-03-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("classes", sa.Column("break_after_slot_1", sa.Integer(), nullable=True))
    op.add_column("classes", sa.Column("break_after_slot_2", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("classes", "break_after_slot_2")
    op.drop_column("classes", "break_after_slot_1")

"""Extra classes: optional staff + preferred slots + consecutive

Revision ID: 004
Revises: 003
Create Date: 2026-03-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("extra_classes", "faculty_id", existing_type=sa.Integer(), nullable=True)
    op.add_column(
        "extra_classes",
        sa.Column("consecutive", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column("extra_classes", sa.Column("preferred_after_slot", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("extra_classes", "preferred_after_slot")
    op.drop_column("extra_classes", "consecutive")
    op.alter_column("extra_classes", "faculty_id", existing_type=sa.Integer(), nullable=False)


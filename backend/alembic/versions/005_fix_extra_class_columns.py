"""Ensure extra_classes new columns exist (safety migration)

Revision ID: 005
Revises: 004
Create Date: 2026-03-17
"""

from typing import Sequence, Union

from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Some environments may have revision stamped without the actual columns.
    op.execute("ALTER TABLE extra_classes ALTER COLUMN faculty_id DROP NOT NULL")
    op.execute("ALTER TABLE extra_classes ADD COLUMN IF NOT EXISTS consecutive boolean NOT NULL DEFAULT false")
    op.execute("ALTER TABLE extra_classes ADD COLUMN IF NOT EXISTS preferred_after_slot integer NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE extra_classes DROP COLUMN IF EXISTS preferred_after_slot")
    op.execute("ALTER TABLE extra_classes DROP COLUMN IF EXISTS consecutive")
    # Can't safely restore NOT NULL if data exists with NULL faculty_id.


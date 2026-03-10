"""GA support: subject type, SubjectFacultyAllocation, ExtraClass, timetable extensions

Revision ID: 002
Revises: 001
Create Date: 2025-03-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("subjects", sa.Column("type", sa.String(length=20), nullable=False, server_default="theory"))

    op.create_table(
        "subject_faculty_allocations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("faculty_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("subject_id", "faculty_id", name="uq_subject_faculty"),
    )
    op.create_index(op.f("ix_subject_faculty_allocations_subject_id"), "subject_faculty_allocations", ["subject_id"], unique=False)
    op.create_index(op.f("ix_subject_faculty_allocations_faculty_id"), "subject_faculty_allocations", ["faculty_id"], unique=False)

    op.create_table(
        "extra_classes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("faculty_id", sa.Integer(), nullable=False),
        sa.Column("hours_per_week", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_extra_classes_class_id"), "extra_classes", ["class_id"], unique=False)
    op.create_index(op.f("ix_extra_classes_faculty_id"), "extra_classes", ["faculty_id"], unique=False)
    op.create_index(op.f("ix_extra_classes_name"), "extra_classes", ["name"], unique=False)

    op.add_column("timetables", sa.Column("extra_class_id", sa.Integer(), nullable=True))
    op.add_column("timetables", sa.Column("faculty_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.create_foreign_key("fk_timetables_extra_class", "timetables", "extra_classes", ["extra_class_id"], ["id"], ondelete="CASCADE")
    op.create_index(op.f("ix_timetables_extra_class_id"), "timetables", ["extra_class_id"], unique=False)
    op.alter_column("timetables", "subject_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("timetables", "faculty_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.alter_column("timetables", "faculty_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("timetables", "subject_id", existing_type=sa.Integer(), nullable=False)
    op.drop_index(op.f("ix_timetables_extra_class_id"), table_name="timetables")
    op.drop_constraint("fk_timetables_extra_class", "timetables", type_="foreignkey")
    op.drop_column("timetables", "faculty_ids")
    op.drop_column("timetables", "extra_class_id")
    op.drop_table("extra_classes")
    op.drop_table("subject_faculty_allocations")
    op.drop_column("subjects", "type")

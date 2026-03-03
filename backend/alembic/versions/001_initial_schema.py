"""Initial schema: faculties, classes, subjects, class_subjects, timetables, faculty_availability

Revision ID: 001
Revises:
Create Date: 2025-03-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "faculties",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_faculties_id"), "faculties", ["id"], unique=False)
    op.create_index(op.f("ix_faculties_name"), "faculties", ["name"], unique=False)

    op.create_table(
        "classes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("working_days", sa.Integer(), nullable=False),
        sa.Column("slots_per_day", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_classes_id"), "classes", ["id"], unique=False)
    op.create_index(op.f("ix_classes_name"), "classes", ["name"], unique=True)

    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("faculty_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculties.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subjects_id"), "subjects", ["id"], unique=False)
    op.create_index(op.f("ix_subjects_name"), "subjects", ["name"], unique=False)
    op.create_index(op.f("ix_subjects_faculty_id"), "subjects", ["faculty_id"], unique=False)

    op.create_table(
        "faculty_availability",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("faculty_id", sa.Integer(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False),
        sa.Column("slot", sa.Integer(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_faculty_availability_faculty_day_slot"), "faculty_availability", ["faculty_id", "day", "slot"], unique=True)
    op.create_index(op.f("ix_faculty_availability_faculty_id"), "faculty_availability", ["faculty_id"], unique=False)

    op.create_table(
        "class_subjects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("hours_per_week", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("class_id", "subject_id", name="uq_class_subject"),
    )
    op.create_index(op.f("ix_class_subjects_class_id"), "class_subjects", ["class_id"], unique=False)
    op.create_index(op.f("ix_class_subjects_subject_id"), "class_subjects", ["subject_id"], unique=False)

    op.create_table(
        "timetables",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False),
        sa.Column("slot", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("faculty_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculties.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("class_id", "day", "slot", name="uq_class_day_slot"),
    )
    op.create_index(op.f("ix_timetables_class_id"), "timetables", ["class_id"], unique=False)
    op.create_index(op.f("ix_timetables_faculty_id"), "timetables", ["faculty_id"], unique=False)
    op.create_index(op.f("ix_timetables_subject_id"), "timetables", ["subject_id"], unique=False)


def downgrade() -> None:
    op.drop_table("timetables")
    op.drop_table("class_subjects")
    op.drop_table("faculty_availability")
    op.drop_table("subjects")
    op.drop_table("classes")
    op.drop_table("faculties")

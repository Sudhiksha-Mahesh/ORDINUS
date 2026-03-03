"""
Subject and class-subject assignment models.
"""
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from core.database import Base


class Subject(Base):
    """Subject taught by a faculty member."""

    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    faculty_id = Column(Integer, ForeignKey("faculties.id", ondelete="SET NULL"), nullable=True, index=True)

    faculty = relationship("Faculty", back_populates="subjects")
    class_subjects = relationship("ClassSubject", back_populates="subject", cascade="all, delete-orphan")
    timetable_entries = relationship("Timetable", back_populates="subject")


class ClassSubject(Base):
    """Links a subject to a class with hours per week."""

    __tablename__ = "class_subjects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    hours_per_week = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("class_id", "subject_id", name="uq_class_subject"),)

    class_ = relationship("Class", back_populates="class_subjects")
    subject = relationship("Subject", back_populates="class_subjects")

"""
Faculty and faculty availability models.
"""
from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from core.database import Base


class Faculty(Base):
    """Faculty member who can teach subjects."""

    __tablename__ = "faculties"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True)

    # Relationships
    availability = relationship("FacultyAvailability", back_populates="faculty", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="faculty")
    timetable_entries = relationship("Timetable", back_populates="faculty")


class FacultyAvailability(Base):
    """Defines when a faculty member is available (day + slot)."""

    __tablename__ = "faculty_availability"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    faculty_id = Column(Integer, ForeignKey("faculties.id", ondelete="CASCADE"), nullable=False, index=True)
    day = Column(Integer, nullable=False)  # 0=Mon, 1=Tue, ...
    slot = Column(Integer, nullable=False)  # 0, 1, 2, ...
    is_available = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_faculty_availability_faculty_day_slot", "faculty_id", "day", "slot", unique=True),
    )

    faculty = relationship("Faculty", back_populates="availability")

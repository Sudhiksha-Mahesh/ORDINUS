"""
Class model (academic class e.g. SS1, SS2).
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from core.database import Base


class Class(Base):
    """Academic class with working days and slots per day."""

    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    working_days = Column(Integer, nullable=False)  # e.g. 5 for Mon-Fri
    slots_per_day = Column(Integer, nullable=False)  # e.g. 8
    # Breaks: 1-based slot number after which a break is shown (e.g. 2 = after 2nd slot)
    break_after_slot_1 = Column(Integer, nullable=True)
    break_after_slot_2 = Column(Integer, nullable=True)

    # Relationships
    class_subjects = relationship("ClassSubject", back_populates="class_", cascade="all, delete-orphan")
    extra_classes = relationship("ExtraClass", back_populates="class_", cascade="all, delete-orphan")
    timetables = relationship("Timetable", back_populates="class_", cascade="all, delete-orphan")

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

    # Relationships
    class_subjects = relationship("ClassSubject", back_populates="class_", cascade="all, delete-orphan")
    timetables = relationship("Timetable", back_populates="class_", cascade="all, delete-orphan")

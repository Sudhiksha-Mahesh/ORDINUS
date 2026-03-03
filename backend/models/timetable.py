"""
Timetable slot model (generated schedule).
"""
from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from core.database import Base


class Timetable(Base):
    """One cell in the timetable: class, day, slot -> subject, faculty."""

    __tablename__ = "timetables"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    day = Column(Integer, nullable=False)  # 0=Mon, 1=Tue, ...
    slot = Column(Integer, nullable=False)  # 0, 1, 2, ...
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    faculty_id = Column(Integer, ForeignKey("faculties.id", ondelete="CASCADE"), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("class_id", "day", "slot", name="uq_class_day_slot"),
    )

    class_ = relationship("Class", back_populates="timetables")
    subject = relationship("Subject", back_populates="timetable_entries")
    faculty = relationship("Faculty", back_populates="timetable_entries")

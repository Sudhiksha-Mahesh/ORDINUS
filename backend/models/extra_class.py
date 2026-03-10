"""
Extra class (PED, Library, Value Education, etc.) per class.
"""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from core.database import Base


class ExtraClass(Base):
    """Extra activity for a class: name, faculty, hours per week."""

    __tablename__ = "extra_classes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    faculty_id = Column(Integer, ForeignKey("faculties.id", ondelete="CASCADE"), nullable=False, index=True)
    hours_per_week = Column(Integer, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    class_ = relationship("Class", back_populates="extra_classes")
    faculty = relationship("Faculty", backref="extra_classes")
    timetable_entries = relationship("Timetable", back_populates="extra_class")

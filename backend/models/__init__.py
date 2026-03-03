"""
SQLAlchemy models for Ordinus.
"""
from models.faculty import Faculty, FacultyAvailability
from models.class_model import Class
from models.subject import Subject, ClassSubject
from models.timetable import Timetable

__all__ = [
    "Faculty",
    "FacultyAvailability",
    "Class",
    "Subject",
    "ClassSubject",
    "Timetable",
]

"""
SQLAlchemy models for Ordinus.
"""
from models.faculty import Faculty, FacultyAvailability
from models.class_model import Class
from models.subject import Subject, ClassSubject, SubjectFacultyAllocation
from models.extra_class import ExtraClass
from models.timetable import Timetable

__all__ = [
    "Faculty",
    "FacultyAvailability",
    "Class",
    "Subject",
    "ClassSubject",
    "SubjectFacultyAllocation",
    "ExtraClass",
    "Timetable",
]

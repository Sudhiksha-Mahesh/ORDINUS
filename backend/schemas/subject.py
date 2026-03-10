"""
Pydantic schemas for Subject and ClassSubject.
"""
from pydantic import BaseModel, Field
from typing import Optional


class SubjectBase(BaseModel):
    """Base schema for subject."""

    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(default="theory", pattern="^(theory|lab)$")
    faculty_id: Optional[int] = None


class SubjectCreate(SubjectBase):
    """Schema for creating a subject."""

    pass


class SubjectUpdate(BaseModel):
    """Schema for updating a subject."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, pattern="^(theory|lab)$")
    faculty_id: Optional[int] = None


class SubjectResponse(SubjectBase):
    """Schema for subject response."""

    id: int

    class Config:
        from_attributes = True


class SubjectWithFacultyResponse(SubjectResponse):
    """Subject with faculty name (for display)."""

    faculty_name: Optional[str] = None


# --- ClassSubject ---


class ClassSubjectBase(BaseModel):
    """Base schema for class-subject assignment."""

    class_id: int
    subject_id: int
    hours_per_week: int = Field(..., ge=1, le=20)


class ClassSubjectCreate(ClassSubjectBase):
    """Schema for creating class-subject."""

    pass


class ClassSubjectCreateForClass(BaseModel):
    """Schema for adding subject to class (class_id from path)."""

    subject_id: int
    hours_per_week: int = Field(..., ge=1, le=20)


class ClassSubjectUpdate(BaseModel):
    """Schema for updating class-subject."""

    hours_per_week: Optional[int] = Field(None, ge=1, le=20)


class ClassSubjectResponse(ClassSubjectBase):
    """Schema for class-subject response."""

    id: int

    class Config:
        from_attributes = True


class ClassSubjectDetailResponse(ClassSubjectResponse):
    """Class-subject with subject name (and optionally faculty)."""

    subject_name: str = ""
    faculty_name: Optional[str] = None

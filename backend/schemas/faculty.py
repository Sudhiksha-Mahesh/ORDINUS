"""
Pydantic schemas for Faculty and FacultyAvailability.
"""
from pydantic import BaseModel, Field
from typing import Optional


class FacultyAvailabilityBase(BaseModel):
    """Base schema for faculty availability."""

    day: int = Field(..., ge=0, description="Day index (0=Mon, 1=Tue, ...)")
    slot: int = Field(..., ge=0, description="Slot index")
    is_available: bool = True


class FacultyAvailabilityCreate(FacultyAvailabilityBase):
    """Schema for creating faculty availability."""

    pass


class FacultyAvailabilityResponse(FacultyAvailabilityBase):
    """Schema for faculty availability response."""

    id: int
    faculty_id: int

    class Config:
        from_attributes = True


class FacultyBase(BaseModel):
    """Base schema for faculty."""

    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)


class FacultyCreate(FacultyBase):
    """Schema for creating a faculty member."""

    pass


class FacultyUpdate(BaseModel):
    """Schema for updating a faculty member."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)


class FacultyResponse(FacultyBase):
    """Schema for faculty response."""

    id: int

    class Config:
        from_attributes = True


class FacultyWithAvailabilityResponse(FacultyResponse):
    """Faculty with list of availability slots."""

    availability: list[FacultyAvailabilityResponse] = []

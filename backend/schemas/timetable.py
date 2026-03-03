"""
Pydantic schemas for Timetable (generated schedule).
"""
from pydantic import BaseModel, Field


class TimetableSlotBase(BaseModel):
    """One slot in the timetable."""

    class_id: int
    day: int
    slot: int
    subject_id: int
    faculty_id: int


class TimetableSlotCreate(TimetableSlotBase):
    """Schema for creating a timetable entry."""

    pass


class TimetableSlotResponse(TimetableSlotBase):
    """Schema for timetable slot response."""

    id: int

    class Config:
        from_attributes = True


class TimetableCellDisplay(BaseModel):
    """One cell for display: subject name + faculty name."""

    subject_name: str
    faculty_name: str


class TimetableGridResponse(BaseModel):
    """Full timetable grid for a class: rows=days, columns=slots."""

    class_id: int
    class_name: str
    working_days: int
    slots_per_day: int
    # grid[row][col] = TimetableCellDisplay; row=day, col=slot
    grid: list[list[TimetableCellDisplay | None]]


class GenerateTimetableRequest(BaseModel):
    """Request to generate timetable (e.g. for which class)."""

    class_id: int = Field(..., description="Class for which to generate timetable")

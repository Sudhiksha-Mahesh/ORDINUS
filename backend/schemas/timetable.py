"""
Pydantic schemas for Timetable (generated schedule).
"""
from typing import Literal

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
    """One cell for display: subject name + faculty name + slot type."""

    subject_name: str
    faculty_name: str
    slot_type: Literal["theory", "lab", "extra"]


class TimetableGridResponse(BaseModel):
    """Full timetable grid for a class: rows=days, columns=slots."""

    class_id: int
    class_name: str
    working_days: int
    slots_per_day: int
    # 1-based slot numbers after which to show a break (e.g. [2, 4] = break after 2nd and 4th slot)
    break_after_slots: list[int] = Field(default_factory=list, description="Break after these slots (1-based)")
    # grid[row][col] = TimetableCellDisplay; row=day, col=slot
    grid: list[list[TimetableCellDisplay | None]]


class GenerateTimetableRequest(BaseModel):
    """Request to generate timetable (e.g. for which class)."""

    class_id: int = Field(..., description="Class for which to generate timetable")


class GenerateTimetableGARequest(BaseModel):
    """Request for GA-based timetable generation."""

    class_id: int = Field(..., description="Class for which to generate timetable")
    population_size: int = Field(default=80, ge=20, le=200)
    generations: int = Field(default=300, ge=100, le=500)
    seed: int | None = Field(default=42, description="Random seed for reproducibility")

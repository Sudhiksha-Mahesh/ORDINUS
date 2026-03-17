"""
Pydantic schemas for Class (academic class).
"""
from pydantic import BaseModel, Field


class ClassBase(BaseModel):
    """Base schema for class."""

    name: str = Field(..., min_length=1, max_length=100)
    working_days: int = Field(..., ge=1, le=7, description="Number of working days per week")
    slots_per_day: int = Field(..., ge=1, le=20, description="Number of slots per day")
    break_after_slot_1: int | None = Field(None, ge=1, le=20, description="Break after this slot (1-based). e.g. 2 = after 2nd slot")
    break_after_slot_2: int | None = Field(None, ge=1, le=20, description="Second break after this slot (1-based). e.g. 4 = after 4th slot")


class ClassCreate(ClassBase):
    """Schema for creating a class."""

    pass


class ClassUpdate(BaseModel):
    """Schema for updating a class."""

    name: str | None = Field(None, min_length=1, max_length=100)
    working_days: int | None = Field(None, ge=1, le=7)
    slots_per_day: int | None = Field(None, ge=1, le=20)
    break_after_slot_1: int | None = Field(None, ge=1, le=20)
    break_after_slot_2: int | None = Field(None, ge=1, le=20)


class ClassResponse(ClassBase):
    """Schema for class response."""

    id: int

    class Config:
        from_attributes = True

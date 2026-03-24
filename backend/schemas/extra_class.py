"""
Extra class schemas.
"""

from pydantic import BaseModel, Field


class ExtraClassBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    faculty_id: int | None = None
    hours_per_week: int = Field(ge=1, le=50)
    consecutive: bool = False
    preferred_after_slot: int | None = Field(default=None, ge=1, le=50)


class ExtraClassCreate(ExtraClassBase):
    class_id: int


class ExtraClassCreateForClass(ExtraClassBase):
    """Create payload when class_id is provided in the path."""

    pass


class ExtraClassUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    faculty_id: int | None = None
    hours_per_week: int | None = Field(default=None, ge=1, le=50)
    consecutive: bool | None = None
    preferred_after_slot: int | None = Field(default=None, ge=1, le=50)


class ExtraClassResponse(BaseModel):
    id: int
    class_id: int
    name: str
    faculty_id: int | None = None
    faculty_name: str | None = None
    hours_per_week: int
    consecutive: bool
    preferred_after_slot: int | None = None

    class Config:
        from_attributes = True


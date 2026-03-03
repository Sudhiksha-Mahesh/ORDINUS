"""
Faculty and faculty availability service layer.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.faculty import Faculty, FacultyAvailability
from schemas.faculty import (
    FacultyCreate,
    FacultyUpdate,
    FacultyAvailabilityCreate,
    FacultyAvailabilityResponse,
    FacultyResponse,
    FacultyWithAvailabilityResponse,
)


async def get_faculty_list(db: AsyncSession) -> list[Faculty]:
    """Return all faculties."""
    result = await db.execute(select(Faculty).order_by(Faculty.name))
    return list(result.scalars().all())


async def get_faculty_by_id(db: AsyncSession, faculty_id: int) -> Faculty | None:
    """Get faculty by id, with availability loaded."""
    result = await db.execute(
        select(Faculty).where(Faculty.id == faculty_id).options(selectinload(Faculty.availability))
    )
    return result.scalar_one_or_none()


async def create_faculty(db: AsyncSession, data: FacultyCreate) -> Faculty:
    """Create a new faculty."""
    faculty = Faculty(name=data.name, email=data.email)
    db.add(faculty)
    await db.flush()
    await db.refresh(faculty)
    return faculty


async def update_faculty(db: AsyncSession, faculty_id: int, data: FacultyUpdate) -> Faculty | None:
    """Update faculty. Returns None if not found."""
    faculty = await get_faculty_by_id(db, faculty_id)
    if not faculty:
        return None
    if data.name is not None:
        faculty.name = data.name
    if data.email is not None:
        faculty.email = data.email
    await db.flush()
    await db.refresh(faculty)
    return faculty


async def delete_faculty(db: AsyncSession, faculty_id: int) -> bool:
    """Delete faculty. Returns True if deleted."""
    faculty = await get_faculty_by_id(db, faculty_id)
    if not faculty:
        return False
    await db.delete(faculty)
    await db.flush()
    return True


# --- Faculty availability ---


async def set_faculty_availability(
    db: AsyncSession, faculty_id: int, slots: list[FacultyAvailabilityCreate]
) -> list[FacultyAvailability]:
    """Replace all availability for a faculty with the given list."""
    faculty = await get_faculty_by_id(db, faculty_id)
    if not faculty:
        return []
    # Remove existing
    for av in faculty.availability:
        await db.delete(av)
    await db.flush()
    # Add new
    new_slots = []
    for s in slots:
        av = FacultyAvailability(
            faculty_id=faculty_id,
            day=s.day,
            slot=s.slot,
            is_available=s.is_available,
        )
        db.add(av)
        new_slots.append(av)
    await db.flush()
    return new_slots


async def get_faculty_availability(db: AsyncSession, faculty_id: int) -> list[FacultyAvailability]:
    """Get all availability entries for a faculty."""
    faculty = await get_faculty_by_id(db, faculty_id)
    if not faculty:
        return []
    return list(faculty.availability)

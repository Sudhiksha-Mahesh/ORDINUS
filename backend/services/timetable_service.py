"""
Timetable generation and retrieval service.
"""
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.timetable import Timetable
from models.class_model import Class
from models.subject import Subject, ClassSubject
from models.faculty import Faculty, FacultyAvailability
from schemas.timetable import TimetableGridResponse, TimetableCellDisplay
from services.class_service import get_class_by_id
from services.scheduler import backtrack_schedule, SubjectDemand, SlotAssignment


async def _get_faculty_availability_for_scheduling(
    db: AsyncSession,
) -> dict[int, list[tuple[int, int]]]:
    """Load all faculty availability as faculty_id -> [(day, slot), ...] (only is_available=True)."""
    result = await db.execute(
        select(FacultyAvailability).where(FacultyAvailability.is_available == True)
    )
    rows = result.scalars().all()
    out: dict[int, list[tuple[int, int]]] = {}
    for r in rows:
        out.setdefault(r.faculty_id, []).append((r.day, r.slot))
    return out


async def generate_timetable_for_class(db: AsyncSession, class_id: int) -> list[Timetable] | None:
    """
    Generate timetable for the given class using backtracking.
    Clears existing timetable for this class and writes new entries.
    Returns list of Timetable rows or None if generation failed.
    """
    class_ = await get_class_by_id(db, class_id)
    if not class_:
        return None
    working_days = class_.working_days
    slots_per_day = class_.slots_per_day

    # Load class_subjects with subject and faculty
    result = await db.execute(
        select(ClassSubject)
        .where(ClassSubject.class_id == class_id)
        .options(
            selectinload(ClassSubject.subject).selectinload(Subject.faculty),
        )
    )
    class_subjects = list(result.scalars().all())
    if not class_subjects:
        return None

    demands: list[SubjectDemand] = []
    for cs in class_subjects:
        if cs.subject.faculty_id is None:
            return None  # Subject must have faculty for scheduling
        demands.append(
            SubjectDemand(
                subject_id=cs.subject_id,
                faculty_id=cs.subject.faculty_id,
                hours_remaining=cs.hours_per_week,
            )
        )

    availability = await _get_faculty_availability_for_scheduling(db)
    assignments = backtrack_schedule(
        working_days=working_days,
        slots_per_day=slots_per_day,
        subject_demands=demands,
        faculty_availability=availability,
    )
    if not assignments:
        return None

    # Delete existing timetable for this class
    await db.execute(delete(Timetable).where(Timetable.class_id == class_id))
    await db.flush()

    # Insert new
    new_entries: list[Timetable] = []
    for a in assignments:
        t = Timetable(
            class_id=class_id,
            day=a.day,
            slot=a.slot,
            subject_id=a.subject_id,
            faculty_id=a.faculty_id,
        )
        db.add(t)
        new_entries.append(t)
    await db.flush()
    return new_entries


async def get_timetable_grid(db: AsyncSession, class_id: int) -> TimetableGridResponse | None:
    """Build grid (rows=days, cols=slots) for display."""
    class_ = await get_class_by_id(db, class_id)
    if not class_:
        return None
    result = await db.execute(
        select(Timetable)
        .where(Timetable.class_id == class_id)
        .options(
            selectinload(Timetable.subject),
            selectinload(Timetable.faculty),
        )
    )
    entries = list(result.scalars().all())
    # Build grid: grid[day][slot] = TimetableCellDisplay | None
    grid: list[list[TimetableCellDisplay | None]] = [
        [None for _ in range(class_.slots_per_day)] for _ in range(class_.working_days)
    ]
    for e in entries:
        if e.day < class_.working_days and e.slot < class_.slots_per_day:
            grid[e.day][e.slot] = TimetableCellDisplay(
                subject_name=e.subject.name,
                faculty_name=e.faculty.name,
            )
    return TimetableGridResponse(
        class_id=class_.id,
        class_name=class_.name,
        working_days=class_.working_days,
        slots_per_day=class_.slots_per_day,
        grid=grid,
    )

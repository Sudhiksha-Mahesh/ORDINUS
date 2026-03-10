"""
Timetable generation and retrieval service.
"""
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.timetable import Timetable
from models.class_model import Class
from models.subject import Subject, ClassSubject, SubjectFacultyAllocation
from models.extra_class import ExtraClass
from models.faculty import Faculty, FacultyAvailability
from schemas.timetable import TimetableGridResponse, TimetableCellDisplay
from services.class_service import get_class_by_id
from services.scheduler import backtrack_schedule, SubjectDemand, SlotAssignment
from services.genetic_scheduler import (
    TheoryDemand,
    LabDemand,
    ExtraDemand,
    run_genetic_algorithm,
    chromosome_to_display_format,
    chromosome_to_slot_assignments,
)


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
    # Faculty with no availability set: treat as available in all class slots
    # so generation can succeed without requiring every faculty to set availability.
    all_slots = [(d, s) for d in range(working_days) for s in range(slots_per_day)]
    faculty_ids_needed = {d.faculty_id for d in demands}
    for fid in faculty_ids_needed:
        if fid not in availability or not availability[fid]:
            availability[fid] = list(all_slots)

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
            selectinload(Timetable.extra_class),
        )
    )
    entries = list(result.scalars().all())
    all_faculty_ids = set()
    for e in entries:
        if e.faculty_id:
            all_faculty_ids.add(e.faculty_id)
        if e.faculty_ids:
            all_faculty_ids.update(e.faculty_ids)
    faculty_names: dict[int, str] = {}
    if all_faculty_ids:
        fac_result = await db.execute(select(Faculty).where(Faculty.id.in_(all_faculty_ids)))
        for f in fac_result.scalars().all():
            faculty_names[f.id] = f.name
    grid: list[list[TimetableCellDisplay | None]] = [
        [None for _ in range(class_.slots_per_day)] for _ in range(class_.working_days)
    ]
    for e in entries:
        if e.day < class_.working_days and e.slot < class_.slots_per_day:
            if e.subject_id and e.subject:
                subject_name = e.subject.name
            elif e.extra_class_id and e.extra_class:
                subject_name = e.extra_class.name
            else:
                subject_name = "?"
            if e.faculty_ids and len(e.faculty_ids) > 0:
                faculty_name = ", ".join(faculty_names.get(fid, "?") for fid in e.faculty_ids)
            elif e.faculty_id and e.faculty:
                faculty_name = e.faculty.name
            else:
                faculty_name = faculty_names.get(e.faculty_id, "") if e.faculty_id else ""
            grid[e.day][e.slot] = TimetableCellDisplay(
                subject_name=subject_name,
                faculty_name=faculty_name,
            )
    return TimetableGridResponse(
        class_id=class_.id,
        class_name=class_.name,
        working_days=class_.working_days,
        slots_per_day=class_.slots_per_day,
        grid=grid,
    )


async def generate_timetable_ga(
    db: AsyncSession,
    class_id: int,
    population_size: int = 80,
    generations: int = 300,
    seed: int | None = 42,
) -> dict | None:
    """
    Generate timetable using Genetic Algorithm.
    Returns { "Monday": [ {"name": "Math", "faculty": ["Staff1"]}, ... ], ... }.
    Persists to Timetable table.
    """
    class_ = await get_class_by_id(db, class_id)
    if not class_:
        return None
    working_days = class_.working_days
    slots_per_day = class_.slots_per_day

    # Load class subjects with type and faculty allocations (for lab)
    result = await db.execute(
        select(ClassSubject)
        .where(ClassSubject.class_id == class_id)
        .options(
            selectinload(ClassSubject.subject).selectinload(Subject.faculty),
            selectinload(ClassSubject.subject).selectinload(Subject.faculty_allocations).selectinload(SubjectFacultyAllocation.faculty),
        )
    )
    class_subjects = list(result.scalars().all())
    theory_demands: list[TheoryDemand] = []
    lab_demands: list[LabDemand] = []
    subject_id_to_name: dict[int, str] = {}
    faculty_id_to_name: dict[int, str] = {}

    for cs in class_subjects:
        subj = cs.subject
        subj_type = getattr(subj, "type", "theory") or "theory"
        subject_id_to_name[subj.id] = subj.name
        if subj.faculty_id:
            faculty_id_to_name[subj.faculty_id] = subj.faculty.name
        if subj_type == "theory":
            if not subj.faculty_id:
                return None
            theory_demands.append(TheoryDemand(subject_id=subj.id, faculty_id=subj.faculty_id, name=subj.name))
        else:
            # Lab: need exactly 2 faculty from allocations or subject.faculty_id + one allocation
            fids = [a.faculty_id for a in subj.faculty_allocations]
            for a in subj.faculty_allocations:
                if getattr(a, "faculty", None):
                    faculty_id_to_name[a.faculty_id] = a.faculty.name
            if subj.faculty_id and subj.faculty_id not in fids:
                fids = [subj.faculty_id] + list(fids)
            if len(fids) < 2:
                return None
            lab_demands.append(LabDemand(subject_id=subj.id, faculty_ids=fids[:2], name=subj.name))

    # Load extra classes for this class
    extra_result = await db.execute(
        select(ExtraClass).where(ExtraClass.class_id == class_id)
    )
    extra_classes = list(extra_result.scalars().all())
    extra_demands: list[ExtraDemand] = []
    extra_id_to_name: dict[int, str] = {}
    for ec in extra_classes:
        extra_demands.append(ExtraDemand(extra_class_id=ec.id, faculty_id=ec.faculty_id, name=ec.name, hours_per_week=ec.hours_per_week))
        extra_id_to_name[ec.id] = ec.name
        faculty_id_to_name[ec.faculty_id] = ""  # will load below if needed

    # Faculty names: load all faculty for this class's subjects and extras
    if not faculty_id_to_name:
        fac_result = await db.execute(select(Faculty))
        for f in fac_result.scalars().all():
            faculty_id_to_name[f.id] = f.name
    else:
        for fid in list(faculty_id_to_name):
            if faculty_id_to_name[fid] == "":
                r = await db.execute(select(Faculty).where(Faculty.id == fid))
                fac = r.scalar_one_or_none()
                if fac:
                    faculty_id_to_name[fid] = fac.name

    availability_list = await _get_faculty_availability_for_scheduling(db)
    all_slots = [(d, s) for d in range(working_days) for s in range(slots_per_day)]
    for d in theory_demands:
        if d.faculty_id not in availability_list or not availability_list[d.faculty_id]:
            availability_list[d.faculty_id] = list(all_slots)
    for d in lab_demands:
        for fid in d.faculty_ids:
            if fid not in availability_list or not availability_list[fid]:
                availability_list[fid] = list(all_slots)
    for d in extra_demands:
        if d.faculty_id not in availability_list or not availability_list[d.faculty_id]:
            availability_list[d.faculty_id] = list(all_slots)
    availability_sets = {fid: set(av) for fid, av in availability_list.items()}

    best = run_genetic_algorithm(
        working_days=working_days,
        slots_per_day=slots_per_day,
        theory_demands=theory_demands,
        lab_demands=lab_demands,
        extra_demands=extra_demands,
        faculty_availability=availability_sets,
        population_size=population_size,
        generations=generations,
        seed=seed,
    )
    if not best:
        return None

    # Persist
    await db.execute(delete(Timetable).where(Timetable.class_id == class_id))
    await db.flush()
    for day, slot, slot_type, ref_id, faculty_ids in chromosome_to_slot_assignments(best, class_id):
        first_fid = faculty_ids[0] if faculty_ids else None
        t = Timetable(
            class_id=class_id,
            day=day,
            slot=slot,
            subject_id=ref_id if slot_type in ("theory", "lab") else None,
            extra_class_id=ref_id if slot_type == "extra" else None,
            faculty_id=first_fid,
            faculty_ids=faculty_ids if len(faculty_ids) > 1 else None,
        )
        db.add(t)
    await db.flush()

    return chromosome_to_display_format(best, subject_id_to_name, extra_id_to_name, faculty_id_to_name)

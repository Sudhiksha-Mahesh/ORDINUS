"""
Subject and class-subject service layer.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.subject import Subject, ClassSubject
from schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
    ClassSubjectCreate,
    ClassSubjectUpdate,
)


async def get_subject_list(db: AsyncSession) -> list[Subject]:
    """Return all subjects with faculty loaded."""
    result = await db.execute(
        select(Subject).options(selectinload(Subject.faculty)).order_by(Subject.name)
    )
    return list(result.scalars().all())


async def get_subject_by_id(db: AsyncSession, subject_id: int) -> Subject | None:
    """Get subject by id."""
    result = await db.execute(
        select(Subject).where(Subject.id == subject_id).options(selectinload(Subject.faculty))
    )
    return result.scalar_one_or_none()


async def create_subject(db: AsyncSession, data: SubjectCreate) -> Subject:
    """Create a new subject."""
    subject = Subject(name=data.name, faculty_id=data.faculty_id)
    db.add(subject)
    await db.flush()
    await db.refresh(subject)
    return subject


async def update_subject(db: AsyncSession, subject_id: int, data: SubjectUpdate) -> Subject | None:
    """Update subject. Returns None if not found."""
    subject = await get_subject_by_id(db, subject_id)
    if not subject:
        return None
    if data.name is not None:
        subject.name = data.name
    if data.faculty_id is not None:
        subject.faculty_id = data.faculty_id
    await db.flush()
    await db.refresh(subject)
    return subject


async def delete_subject(db: AsyncSession, subject_id: int) -> bool:
    """Delete subject. Returns True if deleted."""
    subject = await get_subject_by_id(db, subject_id)
    if not subject:
        return False
    await db.delete(subject)
    await db.flush()
    return True


# --- ClassSubject ---


async def get_class_subjects_for_class(db: AsyncSession, class_id: int) -> list[ClassSubject]:
    """Get all class-subject assignments for a class."""
    result = await db.execute(
        select(ClassSubject)
        .where(ClassSubject.class_id == class_id)
        .options(
            selectinload(ClassSubject.subject).selectinload(Subject.faculty),
        )
        .order_by(ClassSubject.subject_id)
    )
    return list(result.scalars().all())


async def get_class_subject(db: AsyncSession, class_id: int, subject_id: int) -> ClassSubject | None:
    """Get one class-subject by class_id and subject_id."""
    result = await db.execute(
        select(ClassSubject).where(
            ClassSubject.class_id == class_id,
            ClassSubject.subject_id == subject_id,
        )
    )
    return result.scalar_one_or_none()


async def add_class_subject(db: AsyncSession, data: ClassSubjectCreate) -> ClassSubject | None:
    """Add subject to class with hours_per_week. Returns None if class or subject missing."""
    from services.class_service import get_class_by_id
    if await get_class_by_id(db, data.class_id) is None:
        return None
    if await get_subject_by_id(db, data.subject_id) is None:
        return None
    existing = await get_class_subject(db, data.class_id, data.subject_id)
    if existing:
        existing.hours_per_week = data.hours_per_week
        await db.flush()
        await db.refresh(existing)
        return existing
    cs = ClassSubject(
        class_id=data.class_id,
        subject_id=data.subject_id,
        hours_per_week=data.hours_per_week,
    )
    db.add(cs)
    await db.flush()
    await db.refresh(cs)
    return cs


async def update_class_subject(
    db: AsyncSession, class_id: int, subject_id: int, data: ClassSubjectUpdate
) -> ClassSubject | None:
    """Update hours_per_week for a class-subject."""
    cs = await get_class_subject(db, class_id, subject_id)
    if not cs:
        return None
    if data.hours_per_week is not None:
        cs.hours_per_week = data.hours_per_week
    await db.flush()
    await db.refresh(cs)
    return cs


async def remove_class_subject(db: AsyncSession, class_id: int, subject_id: int) -> bool:
    """Remove subject from class."""
    cs = await get_class_subject(db, class_id, subject_id)
    if not cs:
        return False
    await db.delete(cs)
    await db.flush()
    return True

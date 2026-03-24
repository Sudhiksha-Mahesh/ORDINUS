"""
Extra class service layer.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.extra_class import ExtraClass
from schemas.extra_class import ExtraClassCreate, ExtraClassUpdate


async def list_extra_classes_for_class(db: AsyncSession, class_id: int) -> list[ExtraClass]:
    result = await db.execute(
        select(ExtraClass)
        .where(ExtraClass.class_id == class_id)
        .options(selectinload(ExtraClass.faculty))
        .order_by(ExtraClass.name)
    )
    return list(result.scalars().all())


async def get_extra_class_by_id(
    db: AsyncSession, class_id: int, extra_class_id: int
) -> ExtraClass | None:
    result = await db.execute(
        select(ExtraClass)
        .where(ExtraClass.class_id == class_id, ExtraClass.id == extra_class_id)
        .options(selectinload(ExtraClass.faculty))
    )
    return result.scalar_one_or_none()


async def create_extra_class(db: AsyncSession, data: ExtraClassCreate) -> ExtraClass:
    ec = ExtraClass(
        class_id=data.class_id,
        name=data.name.strip(),
        faculty_id=data.faculty_id,
        hours_per_week=data.hours_per_week,
        consecutive=bool(data.consecutive),
        preferred_after_slot=data.preferred_after_slot,
    )
    db.add(ec)
    await db.flush()
    await db.refresh(ec)
    return ec


async def update_extra_class(
    db: AsyncSession, class_id: int, extra_class_id: int, data: ExtraClassUpdate
) -> ExtraClass | None:
    ec = await get_extra_class_by_id(db, class_id, extra_class_id)
    if not ec:
        return None
    if data.name is not None:
        ec.name = data.name.strip()
    if data.faculty_id is not None or data.faculty_id is None:
        # allow explicit null to clear staff assignment
        ec.faculty_id = data.faculty_id
    if data.hours_per_week is not None:
        ec.hours_per_week = data.hours_per_week
    if data.consecutive is not None:
        ec.consecutive = data.consecutive
    if data.preferred_after_slot is not None or data.preferred_after_slot is None:
        ec.preferred_after_slot = data.preferred_after_slot
    await db.flush()
    await db.refresh(ec)
    return ec


async def delete_extra_class(db: AsyncSession, class_id: int, extra_class_id: int) -> bool:
    ec = await get_extra_class_by_id(db, class_id, extra_class_id)
    if not ec:
        return False
    await db.delete(ec)
    await db.flush()
    return True


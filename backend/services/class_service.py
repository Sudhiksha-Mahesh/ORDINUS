"""
Class (academic class) service layer.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.class_model import Class
from schemas.class_schema import ClassCreate, ClassUpdate


async def get_class_list(db: AsyncSession) -> list[Class]:
    """Return all classes."""
    result = await db.execute(select(Class).order_by(Class.name))
    return list(result.scalars().all())


async def get_class_by_id(db: AsyncSession, class_id: int) -> Class | None:
    """Get class by id."""
    result = await db.execute(select(Class).where(Class.id == class_id))
    return result.scalar_one_or_none()


async def create_class(db: AsyncSession, data: ClassCreate) -> Class:
    """Create a new class."""
    class_ = Class(
        name=data.name,
        working_days=data.working_days,
        slots_per_day=data.slots_per_day,
    )
    db.add(class_)
    await db.flush()
    await db.refresh(class_)
    return class_


async def update_class(db: AsyncSession, class_id: int, data: ClassUpdate) -> Class | None:
    """Update class. Returns None if not found."""
    class_ = await get_class_by_id(db, class_id)
    if not class_:
        return None
    if data.name is not None:
        class_.name = data.name
    if data.working_days is not None:
        class_.working_days = data.working_days
    if data.slots_per_day is not None:
        class_.slots_per_day = data.slots_per_day
    await db.flush()
    await db.refresh(class_)
    return class_


async def delete_class(db: AsyncSession, class_id: int) -> bool:
    """Delete class. Returns True if deleted."""
    class_ = await get_class_by_id(db, class_id)
    if not class_:
        return False
    await db.delete(class_)
    await db.flush()
    return True

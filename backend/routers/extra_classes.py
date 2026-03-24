"""
Extra class API (per class).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.extra_class import ExtraClassCreate, ExtraClassCreateForClass, ExtraClassResponse, ExtraClassUpdate
from services import extra_class_service as svc
from services.class_service import get_class_by_id

router = APIRouter(prefix="/classes/{class_id}/extra-classes", tags=["Extra Classes"])


@router.get("", response_model=list[ExtraClassResponse])
async def list_extra_classes(class_id: int, db: AsyncSession = Depends(get_db)):
    if await get_class_by_id(db, class_id) is None:
        raise HTTPException(status_code=404, detail="Class not found")
    items = await svc.list_extra_classes_for_class(db, class_id)
    return [
        ExtraClassResponse(
            id=ec.id,
            class_id=ec.class_id,
            name=ec.name,
            faculty_id=ec.faculty_id,
            faculty_name=ec.faculty.name if getattr(ec, "faculty", None) else None,
            hours_per_week=ec.hours_per_week,
            consecutive=bool(getattr(ec, "consecutive", False)),
            preferred_after_slot=getattr(ec, "preferred_after_slot", None),
        )
        for ec in items
    ]


@router.post("", response_model=ExtraClassResponse, status_code=201)
async def create_extra_class(
    class_id: int, data: ExtraClassCreateForClass, db: AsyncSession = Depends(get_db)
):
    if await get_class_by_id(db, class_id) is None:
        raise HTTPException(status_code=404, detail="Class not found")
    ec = await svc.create_extra_class(
        db,
        ExtraClassCreate(
            class_id=class_id,
            name=data.name,
            faculty_id=data.faculty_id,
            hours_per_week=data.hours_per_week,
            consecutive=data.consecutive,
            preferred_after_slot=data.preferred_after_slot,
        ),
    )
    ec = await svc.get_extra_class_by_id(db, class_id, ec.id)
    return ExtraClassResponse(
        id=ec.id,
        class_id=ec.class_id,
        name=ec.name,
        faculty_id=ec.faculty_id,
        faculty_name=ec.faculty.name if getattr(ec, "faculty", None) else None,
        hours_per_week=ec.hours_per_week,
        consecutive=bool(getattr(ec, "consecutive", False)),
        preferred_after_slot=getattr(ec, "preferred_after_slot", None),
    )


@router.patch("/{extra_class_id}", response_model=ExtraClassResponse)
async def update_extra_class(
    class_id: int,
    extra_class_id: int,
    data: ExtraClassUpdate,
    db: AsyncSession = Depends(get_db),
):
    ec = await svc.update_extra_class(db, class_id, extra_class_id, data)
    if not ec:
        raise HTTPException(status_code=404, detail="Extra class not found")
    ec = await svc.get_extra_class_by_id(db, class_id, extra_class_id)
    return ExtraClassResponse(
        id=ec.id,
        class_id=ec.class_id,
        name=ec.name,
        faculty_id=ec.faculty_id,
        faculty_name=ec.faculty.name if getattr(ec, "faculty", None) else None,
        hours_per_week=ec.hours_per_week,
        consecutive=bool(getattr(ec, "consecutive", False)),
        preferred_after_slot=getattr(ec, "preferred_after_slot", None),
    )


@router.delete("/{extra_class_id}", status_code=204)
async def delete_extra_class(
    class_id: int, extra_class_id: int, db: AsyncSession = Depends(get_db)
):
    ok = await svc.delete_extra_class(db, class_id, extra_class_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Extra class not found")


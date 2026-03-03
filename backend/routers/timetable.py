"""
Timetable generation and display API.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.timetable import GenerateTimetableRequest, TimetableGridResponse
from services import timetable_service as svc

router = APIRouter(prefix="/timetable", tags=["Timetable"])


@router.post("/generate", response_model=dict)
async def generate_timetable(
    body: GenerateTimetableRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate timetable for the given class using backtracking.
    Returns success and message; use GET /timetable/{class_id} to fetch grid.
    """
    entries = await svc.generate_timetable_for_class(db, body.class_id)
    if entries is None:
        raise HTTPException(
            status_code=400,
            detail="Generation failed: check class, subjects, faculty assignment, and faculty availability.",
        )
    return {"success": True, "message": f"Generated {len(entries)} slots.", "class_id": body.class_id}


@router.get("/{class_id}", response_model=TimetableGridResponse)
async def get_timetable(class_id: int, db: AsyncSession = Depends(get_db)):
    """Get timetable grid for a class (rows=days, columns=slots)."""
    grid = await svc.get_timetable_grid(db, class_id)
    if not grid:
        raise HTTPException(status_code=404, detail="Class not found")
    return grid

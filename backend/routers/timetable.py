"""
Timetable generation and display API.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.timetable import (
    GenerateTimetableRequest,
    GenerateTimetableGARequest,
    TimetableGridResponse,
)
from services import timetable_service as svc

router = APIRouter(prefix="/timetable", tags=["Timetable"])


@router.post("/generate", response_model=dict)
async def generate_timetable(
    body: GenerateTimetableRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate timetable for the given class using backtracking (subjects), then place
    extra-class slots from configured extra classes (hours/week, consecutive, preferred slot).
    Returns success and message; use GET /timetable/{class_id} to fetch grid.
    """
    entries = await svc.generate_timetable_for_class(db, body.class_id)
    if entries is None:
        raise HTTPException(
            status_code=400,
            detail="Generation failed: check class, subjects, faculty assignment, and faculty availability.",
        )
    return {"success": True, "message": f"Generated {len(entries)} slots.", "class_id": body.class_id}


@router.post("/generate-ga", response_model=dict)
async def generate_timetable_ga(
    body: GenerateTimetableGARequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate timetable using Genetic Algorithm.
    Returns { "Monday": [ {"name": "Math", "faculty": ["Staff1"]}, ... ], ... }.
    Theory: 3 hrs/week max 1/day, 1 faculty. Lab: 4 hrs as 2+2 consecutive, 2 faculty.
    Extra classes: hours/week, max 2 extra slots/day (adjacent), after teaching, preferred-after,
    consecutive chunks without breaks; timetable rows have no internal gaps (GA objective).
    Persists to DB.
    """
    try:
        return await svc.generate_timetable_ga(
            db,
            body.class_id,
            population_size=body.population_size,
            generations=body.generations,
            seed=body.seed,
        )
    except ValueError as e:
        msg = str(e)
        status = 404 if msg.startswith("Class not found") else 400
        raise HTTPException(status_code=status, detail=msg) from e


@router.get("/{class_id}", response_model=TimetableGridResponse)
async def get_timetable(class_id: int, db: AsyncSession = Depends(get_db)):
    """Get timetable grid for a class (rows=days, columns=slots)."""
    grid = await svc.get_timetable_grid(db, class_id)
    if not grid:
        raise HTTPException(status_code=404, detail="Class not found")
    return grid

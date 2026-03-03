"""
Faculty and faculty availability API.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.faculty import (
    FacultyCreate,
    FacultyUpdate,
    FacultyResponse,
    FacultyWithAvailabilityResponse,
    FacultyAvailabilityCreate,
    FacultyAvailabilityResponse,
)
from services import faculty_service as svc

router = APIRouter(prefix="/faculties", tags=["Faculty"])


@router.get("", response_model=list[FacultyResponse])
async def list_faculties(db: AsyncSession = Depends(get_db)):
    """List all faculties."""
    faculties = await svc.get_faculty_list(db)
    return [FacultyResponse.model_validate(f) for f in faculties]


@router.get("/{faculty_id}", response_model=FacultyWithAvailabilityResponse)
async def get_faculty(faculty_id: int, db: AsyncSession = Depends(get_db)):
    """Get faculty by id with availability."""
    faculty = await svc.get_faculty_by_id(db, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return FacultyWithAvailabilityResponse(
        id=faculty.id,
        name=faculty.name,
        email=faculty.email,
        availability=[
            FacultyAvailabilityResponse(
                id=a.id,
                faculty_id=a.faculty_id,
                day=a.day,
                slot=a.slot,
                is_available=a.is_available,
            )
            for a in faculty.availability
        ],
    )


@router.post("", response_model=FacultyResponse, status_code=201)
async def create_faculty(data: FacultyCreate, db: AsyncSession = Depends(get_db)):
    """Create a new faculty."""
    faculty = await svc.create_faculty(db, data)
    return FacultyResponse.model_validate(faculty)


@router.patch("/{faculty_id}", response_model=FacultyResponse)
async def update_faculty(
    faculty_id: int, data: FacultyUpdate, db: AsyncSession = Depends(get_db)
):
    """Update faculty."""
    faculty = await svc.update_faculty(db, faculty_id, data)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return FacultyResponse.model_validate(faculty)


@router.delete("/{faculty_id}", status_code=204)
async def delete_faculty(faculty_id: int, db: AsyncSession = Depends(get_db)):
    """Delete faculty."""
    ok = await svc.delete_faculty(db, faculty_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Faculty not found")


@router.put("/{faculty_id}/availability", response_model=list[FacultyAvailabilityResponse])
async def set_availability(
    faculty_id: int,
    slots: list[FacultyAvailabilityCreate],
    db: AsyncSession = Depends(get_db),
):
    """Set faculty availability (replaces existing)."""
    updated = await svc.set_faculty_availability(db, faculty_id, slots)
    if not updated and await svc.get_faculty_by_id(db, faculty_id) is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return [
        FacultyAvailabilityResponse(
            id=a.id,
            faculty_id=a.faculty_id,
            day=a.day,
            slot=a.slot,
            is_available=a.is_available,
        )
        for a in updated
    ]

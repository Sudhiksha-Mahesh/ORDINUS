"""
Subject and class-subject API.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    SubjectWithFacultyResponse,
    ClassSubjectCreateForClass,
    ClassSubjectUpdate,
    ClassSubjectResponse,
    ClassSubjectDetailResponse,
)
from services import subject_service as svc

router = APIRouter(prefix="/subjects", tags=["Subject"])


@router.get("", response_model=list[SubjectWithFacultyResponse])
async def list_subjects(db: AsyncSession = Depends(get_db)):
    """List all subjects."""
    subjects = await svc.get_subject_list(db)
    return [
        SubjectWithFacultyResponse(
            id=s.id,
            name=s.name,
            type=getattr(s, "type", "theory"),
            faculty_id=s.faculty_id,
            faculty_name=s.faculty.name if s.faculty else None,
        )
        for s in subjects
    ]


@router.get("/{subject_id}", response_model=SubjectWithFacultyResponse)
async def get_subject(subject_id: int, db: AsyncSession = Depends(get_db)):
    """Get subject by id."""
    subject = await svc.get_subject_by_id(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return SubjectWithFacultyResponse(
        id=subject.id,
        name=subject.name,
        faculty_id=subject.faculty_id,
        faculty_name=subject.faculty.name if subject.faculty else None,
    )


@router.post("", response_model=SubjectResponse, status_code=201)
async def create_subject(data: SubjectCreate, db: AsyncSession = Depends(get_db)):
    """Create a new subject."""
    subject = await svc.create_subject(db, data)
    return SubjectResponse.model_validate(subject)


@router.patch("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: int, data: SubjectUpdate, db: AsyncSession = Depends(get_db)
):
    """Update subject."""
    subject = await svc.update_subject(db, subject_id, data)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return SubjectResponse.model_validate(subject)


@router.delete("/{subject_id}", status_code=204)
async def delete_subject(subject_id: int, db: AsyncSession = Depends(get_db)):
    """Delete subject."""
    ok = await svc.delete_subject(db, subject_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Subject not found")


# --- Class-Subject (assign subject to class with hours) ---


@router.get(
    "/classes/{class_id}",
    response_model=list[ClassSubjectDetailResponse],
)
async def list_class_subjects(class_id: int, db: AsyncSession = Depends(get_db)):
    """List all subjects assigned to a class with hours per week."""
    items = await svc.get_class_subjects_for_class(db, class_id)
    return [
        ClassSubjectDetailResponse(
            id=cs.id,
            class_id=cs.class_id,
            subject_id=cs.subject_id,
            hours_per_week=cs.hours_per_week,
            subject_name=cs.subject.name,
            faculty_name=cs.subject.faculty.name if cs.subject.faculty else None,
        )
        for cs in items
    ]


@router.post(
    "/classes/{class_id}/subjects",
    response_model=ClassSubjectResponse,
    status_code=201,
)
async def add_subject_to_class(
    class_id: int, data: ClassSubjectCreateForClass, db: AsyncSession = Depends(get_db)
):
    """Assign subject to class with hours per week. Body: subject_id, hours_per_week."""
    from schemas.subject import ClassSubjectCreate
    create_data = ClassSubjectCreate(
        class_id=class_id,
        subject_id=data.subject_id,
        hours_per_week=data.hours_per_week,
    )
    cs = await svc.add_class_subject(db, create_data)
    if not cs:
        raise HTTPException(
            status_code=404,
            detail="Class or subject not found, or invalid assignment",
        )
    return ClassSubjectResponse.model_validate(cs)


@router.patch(
    "/classes/{class_id}/subjects/{subject_id}",
    response_model=ClassSubjectResponse,
)
async def update_class_subject(
    class_id: int,
    subject_id: int,
    data: ClassSubjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update hours per week for a class-subject."""
    cs = await svc.update_class_subject(db, class_id, subject_id, data)
    if not cs:
        raise HTTPException(status_code=404, detail="Class-subject not found")
    return ClassSubjectResponse.model_validate(cs)


@router.delete("/classes/{class_id}/subjects/{subject_id}", status_code=204)
async def remove_subject_from_class(
    class_id: int, subject_id: int, db: AsyncSession = Depends(get_db)
):
    """Remove subject from class."""
    ok = await svc.remove_class_subject(db, class_id, subject_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Class-subject not found")

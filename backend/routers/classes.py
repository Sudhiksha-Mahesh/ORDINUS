"""
Class (academic class) API.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.class_schema import ClassCreate, ClassUpdate, ClassResponse
from services import class_service as svc

router = APIRouter(prefix="/classes", tags=["Class"])


@router.get("", response_model=list[ClassResponse])
async def list_classes(db: AsyncSession = Depends(get_db)):
    """List all classes."""
    classes = await svc.get_class_list(db)
    return [ClassResponse.model_validate(c) for c in classes]


@router.get("/{class_id}", response_model=ClassResponse)
async def get_class(class_id: int, db: AsyncSession = Depends(get_db)):
    """Get class by id."""
    class_ = await svc.get_class_by_id(db, class_id)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return ClassResponse.model_validate(class_)


@router.post("", response_model=ClassResponse, status_code=201)
async def create_class(data: ClassCreate, db: AsyncSession = Depends(get_db)):
    """Create a new class."""
    class_ = await svc.create_class(db, data)
    return ClassResponse.model_validate(class_)


@router.patch("/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: int, data: ClassUpdate, db: AsyncSession = Depends(get_db)
):
    """Update class."""
    class_ = await svc.update_class(db, class_id, data)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return ClassResponse.model_validate(class_)


@router.delete("/{class_id}", status_code=204)
async def delete_class(class_id: int, db: AsyncSession = Depends(get_db)):
    """Delete class."""
    ok = await svc.delete_class(db, class_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Class not found")

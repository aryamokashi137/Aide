from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.api.v1.endpoints.deps import get_current_user
from app.models.visit import Visit, VisitStatus
from app.schemas.visit import VisitCreate, VisitResponse, VisitUpdate
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
def create_visit(
    visit_in: VisitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Schedule a new visit for a student (PG, College, school, etc.)
    """
    visit = Visit(
        user_id=current_user.id,
        entity_type=visit_in.entity_type,
        entity_id=visit_in.entity_id,
        entity_name=visit_in.entity_name,
        visit_date=visit_in.visit_date,
        preferred_time=visit_in.preferred_time,
        message=visit_in.message,
        status=VisitStatus.PENDING
    )
    
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit

@router.get("/me", response_model=List[VisitResponse])
def get_my_visits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all visits scheduled by the current student.
    """
    return db.query(Visit).filter(
        Visit.user_id == current_user.id, 
        Visit.is_active == True
    ).order_by(Visit.visit_date.asc()).all()

@router.get("/{visit_id}", response_model=VisitResponse)
def get_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit or (visit.user_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit

@router.patch("/{visit_id}", response_model=VisitResponse)
def update_visit(
    visit_id: int,
    visit_update: VisitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit or (visit.user_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=404, detail="Visit not found")
    
    if visit_update.status:
        visit.status = visit_update.status
    if visit_update.visit_date:
        visit.visit_date = visit_update.visit_date
    if visit_update.message:
        visit.message = visit_update.message
        
    db.commit()
    db.refresh(visit)
    return visit

@router.delete("/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit or (visit.user_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=404, detail="Visit not found")
    
    visit.status = VisitStatus.CANCELLED
    visit.is_active = False 
    db.commit()
    return None

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.education.review import Review
from app.schemas.education.review import ReviewCreate, ReviewResponse
from enum import Enum

class TargetType(str, Enum):
    COLLEGE = "college"
    SCHOOL = "school"
    HOSTEL = "hostel"
    MESS = "mess"
    COACHING = "coaching"
    PG = "pg"

router = APIRouter()

@router.post("/", response_model=ReviewResponse)
def create_review(
    review_in: ReviewCreate,
    target_type: TargetType = Query(...),
    target_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = Review(
        user_id=current_user.id,
        content=review_in.content,
        rating=review_in.rating,
    )
    
    # Map target
    if target_type == TargetType.COLLEGE: review.college_id = target_id
    elif target_type == TargetType.SCHOOL: review.school_id = target_id
    elif target_type == TargetType.HOSTEL: review.hostel_id = target_id
    elif target_type == TargetType.MESS: review.mess_id = target_id
    elif target_type == TargetType.COACHING: review.coaching_id = target_id
    elif target_type == TargetType.PG: review.pg_id = target_id
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    return review

@router.get("/{target_type}/{target_id}", response_model=List[ReviewResponse])
def get_reviews(
    target_type: TargetType,
    target_id: int,
    db: Session = Depends(get_db)
):
    query = db.query(Review)
    
    if target_type == TargetType.COLLEGE: query = query.filter(Review.college_id == target_id)
    elif target_type == TargetType.SCHOOL: query = query.filter(Review.school_id == target_id)
    elif target_type == TargetType.HOSTEL: query = query.filter(Review.hostel_id == target_id)
    elif target_type == TargetType.MESS: query = query.filter(Review.mess_id == target_id)
    elif target_type == TargetType.COACHING: query = query.filter(Review.coaching_id == target_id)
    elif target_type == TargetType.PG: query = query.filter(Review.pg_id == target_id)
    
    return query.all()

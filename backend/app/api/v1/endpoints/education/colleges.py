from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.education.review import Review
from app.schemas.education.review import ReviewCreate, ReviewResponse

from app.core.logger import logger
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.education.colleges import College, CollegeType
from app.schemas.education.colleges import (
    CollegeCreate,
    CollegeUpdate,
    CollegeResponse
)
from app.api.v1.endpoints.deps import get_current_user, require_roles


router = APIRouter(
    prefix="/colleges",
    tags=["Colleges"]
)

from app.core.location import calculate_haversine_distance

@router.get("/", response_model=List[CollegeResponse])
async def get_colleges(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    lat: Optional[float] = Query(None, description="User's current latitude"),
    lon: Optional[float] = Query(None, description="User's current longitude"),
    radius: Optional[float] = Query(None, description="Radius in km", ge=0.1),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get colleges with optional name/type filtering and nearby search.
    """
    query = db.query(College).filter(College.is_active == True)
    if name:
        query = query.filter(College.name.ilike(f"%{name}%"))
    if type:
        query = query.filter(College.type.ilike(f"%{type}%"))
    
    # Execute query
    colleges = query.all()
    
    # Logic for nearby search
    if lat is not None and lon is not None:
        nearby_colleges = []
        for college in colleges:
            if college.latitude and college.longitude:
                dist = calculate_haversine_distance(lat, lon, college.latitude, college.longitude)
                college.distance = round(dist, 2)
                
                if radius is None or dist <= radius:
                    nearby_colleges.append(college)
        
        nearby_colleges.sort(key=lambda x: x.distance)
        return nearby_colleges[skip : skip + limit]
        
    # Standard pagination
    return query.offset(skip).limit(limit).all()

@router.get("/{college_id}", response_model=CollegeResponse)
async def get_college(
    college_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    college = db.query(College).filter(
        College.id == college_id, College.is_active == True
    ).first()

    if not college:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="College not found"
        )

    return college

@router.post("/", response_model=CollegeResponse, status_code=201)
async def create_college(
    college_data: CollegeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    # Check duplicate name
    existing_college = db.query(College).filter(
        College.name == college_data.name
    ).first()

    if existing_college:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="College with this name already exists"
        )

    # Convert request model to plain data. use jsonable_encoder so that
    # HttpUrl values (which are pydantic Url objects) turn into strings
    # before we hand them to SQLAlchemy. otherwise psycopg2 raises
    # "can't adapt type 'pydantic_core._pydantic_core.Url'".
    from fastapi.encoders import jsonable_encoder

    college_dict = jsonable_encoder(college_data)

    # Convert type string → Enum
    if college_dict.get("type"):
        try:
            college_dict["type"] = CollegeType(college_dict["type"])
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid college type"
            )

    college = College(**college_dict)

    db.add(college)
    db.commit()
    db.refresh(college)

    return college

@router.patch("/{college_id}", response_model=CollegeResponse)
async def update_college(
    college_id: int,
    college_data: CollegeUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    college = db.query(College).filter(College.id == college_id).first()

    if not college:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="College not found"
        )

    # encode model to plain data (handles Url → str, etc.)
    from fastapi.encoders import jsonable_encoder
    update_data = jsonable_encoder(college_data, exclude_unset=True)

    # check for duplicate name or code if they are being changed
    if "name" in update_data and update_data["name"] != college.name:
        dup = db.query(College).filter(College.name == update_data["name"]).first()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="College with this name already exists"
            )
    if "college_code" in update_data and update_data["college_code"] != college.college_code:
        dup = db.query(College).filter(College.college_code == update_data["college_code"]).first()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="College with this code already exists"
            )

    if "type" in update_data:
        try:
            update_data["type"] = CollegeType(update_data["type"])
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid college type"
            )

    for key, value in update_data.items():
        setattr(college, key, value)

    db.commit()
    db.refresh(college)

    return college

@router.delete("/{college_id}", status_code=204)
async def delete_college(
    college_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    college = db.query(College).filter(College.id == college_id).first()

    if not college:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="College not found"
        )

    # Soft delete
    college.is_active = False
    db.commit()

    return None



# ------------------- REVIEWS -------------------
@router.get("/{college_id}/reviews", response_model=List[ReviewResponse])
async def get_college_reviews(
    college_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(
        Review.college_id == college_id, Review.is_active == True
    ).offset(skip).limit(limit).all()
    return reviews


@router.post("/{college_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_college_review(
    college_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    entity = db.query(College).filter(College.id == college_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="College not found")
        
    review_dict = review_data.model_dump()
    review_dict["user_id"] = current_user.id
    review_dict["college_id"] = college_id
    
    review = Review(**review_dict)
    db.add(review)
    db.commit()
    db.refresh(review)
    
    logger.info(f"Review added to College {college_id} by user {current_user.id}")
    return review

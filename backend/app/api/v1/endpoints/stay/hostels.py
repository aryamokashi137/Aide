from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.education.review import Review
from app.schemas.education.review import ReviewCreate, ReviewResponse

from app.core.logger import logger
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.stay.hostels import Hostel, GenderType, RoomType
from app.schemas.stay.hostels import (
    HostelCreate,
    HostelUpdate,
    HostelResponse
)
from app.api.v1.endpoints.deps import get_current_user, require_roles
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/hostels",
    tags=["Hostels"]
)

from app.core.location import calculate_haversine_distance

@router.get("/", response_model=List[HostelResponse])
async def get_hostels(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    lat: Optional[float] = Query(None, description="User's current latitude"),
    lon: Optional[float] = Query(None, description="User's current longitude"),
    radius: Optional[float] = Query(None, description="Radius in km", ge=0.1),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get hostels with optional name/gender filtering and nearby search.
    """
    query = db.query(Hostel).filter(Hostel.is_active == True)
    if name:
        query = query.filter(Hostel.name.ilike(f"%{name}%"))
    if gender:
        query = query.filter(Hostel.gender == gender)
    
    # Execute query
    hostels = query.all()
    
    # Logic for nearby search
    if lat is not None and lon is not None:
        nearby_hostels = []
        for hostel in hostels:
            if hostel.latitude and hostel.longitude:
                dist = calculate_haversine_distance(lat, lon, hostel.latitude, hostel.longitude)
                hostel.distance = round(dist, 2)
                
                if radius is None or dist <= radius:
                    nearby_hostels.append(hostel)
        
        nearby_hostels.sort(key=lambda x: x.distance)
        return nearby_hostels[skip : skip + limit]
        
    # Standard pagination
    return query.offset(skip).limit(limit).all()

@router.get("/{hostel_id}", response_model=HostelResponse)
async def get_hostel(
    hostel_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id, Hostel.is_active == True).first()
    if not hostel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hostel not found"
        )
    return hostel

@router.post("/", response_model=HostelResponse, status_code=status.HTTP_201_CREATED)
async def create_hostel(
    hostel_data: HostelCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    existing_hostel = db.query(Hostel).filter(Hostel.name == hostel_data.name).first()
    if existing_hostel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hostel with this name already exists"
        )

    hostel_dict = jsonable_encoder(hostel_data)
    
    if "gender" in hostel_dict and hostel_dict["gender"]:
        try:
            hostel_dict["gender"] = GenderType(hostel_dict["gender"])
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid gender type")
            
    if "room_type" in hostel_dict and hostel_dict["room_type"]:
        try:
            hostel_dict["room_type"] = RoomType(hostel_dict["room_type"])
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid room type")

    hostel = Hostel(**hostel_dict)
    db.add(hostel)
    db.commit()
    db.refresh(hostel)
    logger.info(f"Hostel created successfully: {hostel.name} by user {current_user.id}")
    return hostel

@router.patch("/{hostel_id}", response_model=HostelResponse)
async def update_hostel(
    hostel_id: int,
    hostel_data: HostelUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id, Hostel.is_active == True).first()
    if not hostel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hostel not found"
        )

    update_data = jsonable_encoder(hostel_data, exclude_unset=True)

    if "name" in update_data and update_data["name"] != hostel.name:
        dup = db.query(Hostel).filter(Hostel.name == update_data["name"]).first()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hostel with this name already exists"
            )

    if "gender" in update_data and update_data["gender"]:
        try:
            update_data["gender"] = GenderType(update_data["gender"])
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid gender type")
            
    if "room_type" in update_data and update_data["room_type"]:
        try:
            update_data["room_type"] = RoomType(update_data["room_type"])
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid room type")

    for key, value in update_data.items():
        setattr(hostel, key, value)

    db.commit()
    db.refresh(hostel)
    logger.info(f"Hostel updated successfully: {hostel.name} by user {current_user.id}")
    return hostel

@router.delete("/{hostel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hostel(
    hostel_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id, Hostel.is_active == True).first()
    if not hostel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hostel not found"
        )
    
    hostel.is_active = False
    db.commit()
    logger.info(f"Hostel deleted successfully: {hostel.id} by user {current_user.id}")
    return None


# ------------------- REVIEWS -------------------
@router.get("/{hostel_id}/reviews", response_model=List[ReviewResponse])
async def get_hostel_reviews(
    hostel_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(
        Review.hostel_id == hostel_id, Review.is_active == True
    ).offset(skip).limit(limit).all()
    return reviews


@router.post("/{hostel_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_hostel_review(
    hostel_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    entity = db.query(Hostel).filter(Hostel.id == hostel_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel not found")
        
    review_dict = review_data.model_dump()
    review_dict["user_id"] = current_user.id
    review_dict["hostel_id"] = hostel_id
    
    review = Review(**review_dict)
    db.add(review)
    db.commit()
    db.refresh(review)
    
    logger.info(f"Review added to Hostel {hostel_id} by user {current_user.id}")
    return review

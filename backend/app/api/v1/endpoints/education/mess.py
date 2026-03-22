from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.education.review import Review
from app.schemas.education.review import ReviewCreate, ReviewResponse

from app.core.logger import logger
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.education.mess import Mess, MessType
from app.schemas.education.mess import (
    MessCreate,
    MessUpdate,
    MessResponse
)
from app.api.v1.endpoints.deps import get_current_user, require_roles
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/mess",
    tags=["Mess"]
)

from app.core.location import calculate_haversine_distance

# ------------------- GET ALL -------------------
@router.get("/", response_model=List[MessResponse])
async def get_mess_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    lat: Optional[float] = Query(None, description="User's current latitude"),
    lon: Optional[float] = Query(None, description="User's current longitude"),
    radius: Optional[float] = Query(None, description="Radius in km", ge=0.1),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get mess list with optional name filtering and nearby search.
    """
    query = db.query(Mess).filter(Mess.is_active == True)
    if name:
        query = query.filter(Mess.name.ilike(f"%{name}%"))
    
    # Execute query
    mess_list = query.all()
    
    # Logic for nearby search
    if lat is not None and lon is not None:
        nearby_mess = []
        for mess in mess_list:
            if mess.latitude and mess.longitude:
                dist = calculate_haversine_distance(lat, lon, mess.latitude, mess.longitude)
                mess.distance = round(dist, 2)
                
                if radius is None or dist <= radius:
                    nearby_mess.append(mess)
        
        nearby_mess.sort(key=lambda x: x.distance)
        return nearby_mess[skip : skip + limit]
        
    # Standard pagination
    return query.offset(skip).limit(limit).all()

# ------------------- GET ONE -------------------
@router.get("/{mess_id}", response_model=MessResponse)
async def get_mess(
    mess_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    mess = db.query(Mess).filter(Mess.id == mess_id, Mess.is_active == True).first()

    if not mess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mess not found"
        )
    return mess

# ------------------- CREATE -------------------
@router.post("/", response_model=MessResponse, status_code=status.HTTP_201_CREATED)
async def create_mess(
    mess_data: MessCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    # Check duplicate name
    existing_mess = db.query(Mess).filter(Mess.name == mess_data.name).first()
    if existing_mess:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mess with this name already exists"
        )

    mess_dict = jsonable_encoder(mess_data)

    # Convert meal_types string → Enum
    if mess_dict.get("meal_types"):
        try:
            mess_dict["meal_types"] = MessType(mess_dict["meal_types"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid meal type"
            )

    mess = Mess(**mess_dict)
    db.add(mess)
    db.commit()
    db.refresh(mess)

    return mess

# ------------------- UPDATE -------------------
@router.patch("/{mess_id}", response_model=MessResponse)
async def update_mess(
    mess_id: int,
    mess_data: MessUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    mess = db.query(Mess).filter(Mess.id == mess_id, Mess.is_active == True).first()

    if not mess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mess not found"
        )

    update_data = jsonable_encoder(mess_data, exclude_unset=True)

    # Check for duplicate name
    if "name" in update_data and update_data["name"] != mess.name:
        dup = db.query(Mess).filter(Mess.name == update_data["name"]).first()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mess with this name already exists"
            )

    # Enum conversion
    if "meal_types" in update_data:
        try:
            update_data["meal_types"] = MessType(update_data["meal_types"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid meal type"
            )

    for key, value in update_data.items():
        setattr(mess, key, value)

    db.commit()
    db.refresh(mess)
    return mess

# ------------------- DELETE -------------------
@router.delete("/{mess_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mess(
    mess_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    mess = db.query(Mess).filter(Mess.id == mess_id, Mess.is_active == True).first()

    if not mess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mess not found"
        )

    # Soft delete
    mess.is_active = False
    db.commit()
    return None


# ------------------- REVIEWS -------------------
@router.get("/{mess_id}/reviews", response_model=List[ReviewResponse])
async def get_mess_reviews(
    mess_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(
        Review.mess_id == mess_id, Review.is_active == True
    ).offset(skip).limit(limit).all()
    return reviews


@router.post("/{mess_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_mess_review(
    mess_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    entity = db.query(Mess).filter(Mess.id == mess_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mess not found")
        
    review_dict = review_data.model_dump()
    review_dict["user_id"] = current_user.id
    review_dict["mess_id"] = mess_id
    
    review = Review(**review_dict)
    db.add(review)
    db.commit()
    db.refresh(review)
    
    logger.info(f"Review added to Mess {mess_id} by user {current_user.id}")
    return review

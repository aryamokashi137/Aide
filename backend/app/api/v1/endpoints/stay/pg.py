from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.education.review import Review
from app.schemas.education.review import ReviewCreate, ReviewResponse

from app.core.logger import logger
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.stay.pg import PG, GenderType, RoomType
from app.schemas.stay.pg import (
    PGCreate,
    PGUpdate,
    PGResponse
)
from app.api.v1.endpoints.deps import get_current_user, require_roles
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/pgs",
    tags=["PGs"]
)

from app.core.location import calculate_haversine_distance

@router.get("/", response_model=List[PGResponse])
async def get_pgs(
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
    Get PGs with optional name/gender filtering and nearby search.
    """
    query = db.query(PG).filter(PG.is_active == True)
    if name:
        query = query.filter(PG.name.ilike(f"%{name}%"))
    if gender:
        query = query.filter(PG.gender == gender)
    
    # Execute query
    pgs = query.all()
    
    # Logic for nearby search
    if lat is not None and lon is not None:
        nearby_pgs = []
        for pg in pgs:
            if pg.latitude and pg.longitude:
                dist = calculate_haversine_distance(lat, lon, pg.latitude, pg.longitude)
                pg.distance = round(dist, 2)
                
                if radius is None or dist <= radius:
                    nearby_pgs.append(pg)
        
        nearby_pgs.sort(key=lambda x: x.distance)
        return nearby_pgs[skip : skip + limit]
        
    # Standard pagination
    return query.offset(skip).limit(limit).all()

@router.get("/{pg_id}", response_model=PGResponse)
async def get_pg(
    pg_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    pg = db.query(PG).filter(PG.id == pg_id, PG.is_active == True).first()
    if not pg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PG not found"
        )
    return pg

@router.post("/", response_model=PGResponse, status_code=status.HTTP_201_CREATED)
async def create_pg(
    pg_data: PGCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    existing_pg = db.query(PG).filter(PG.name == pg_data.name).first()
    if existing_pg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PG with this name already exists"
        )

    pg_dict = jsonable_encoder(pg_data)
    
    if "gender" in pg_dict and pg_dict["gender"]:
        try:
            pg_dict["gender"] = GenderType(pg_dict["gender"])
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid gender type")
            
    if "room_type" in pg_dict and pg_dict["room_type"]:
        try:
            pg_dict["room_type"] = RoomType(pg_dict["room_type"])
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid room type")

    pg = PG(**pg_dict)
    db.add(pg)
    db.commit()
    db.refresh(pg)
    logger.info(f"PG created successfully: {pg.name} by user {current_user.id}")
    return pg

@router.patch("/{pg_id}", response_model=PGResponse)
async def update_pg(
    pg_id: int,
    pg_data: PGUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    pg = db.query(PG).filter(PG.id == pg_id, PG.is_active == True).first()
    if not pg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PG not found"
        )

    update_data = jsonable_encoder(pg_data, exclude_unset=True)

    if "name" in update_data and update_data["name"] != pg.name:
        dup = db.query(PG).filter(PG.name == update_data["name"]).first()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PG with this name already exists"
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
        setattr(pg, key, value)

    db.commit()
    db.refresh(pg)
    logger.info(f"PG updated successfully: {pg.name} by user {current_user.id}")
    return pg

@router.delete("/{pg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pg(
    pg_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    pg = db.query(PG).filter(PG.id == pg_id, PG.is_active == True).first()
    if not pg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PG not found"
        )
    
    pg.is_active = False
    db.commit()
    logger.info(f"PG deleted successfully: {pg.id} by user {current_user.id}")
    return None


# ------------------- REVIEWS -------------------
@router.get("/{pg_id}/reviews", response_model=List[ReviewResponse])
async def get_pg_reviews(
    pg_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(
        Review.pg_id == pg_id, Review.is_active == True
    ).offset(skip).limit(limit).all()
    return reviews


@router.post("/{pg_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_pg_review(
    pg_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    entity = db.query(PG).filter(PG.id == pg_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PG not found")
        
    review_dict = review_data.model_dump()
    review_dict["user_id"] = current_user.id
    review_dict["pg_id"] = pg_id
    
    review = Review(**review_dict)
    db.add(review)
    db.commit()
    db.refresh(review)
    
    logger.info(f"Review added to PG {pg_id} by user {current_user.id}")
    return review

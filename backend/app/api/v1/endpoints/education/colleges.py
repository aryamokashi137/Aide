from fastapi import APIRouter, Depends, HTTPException, status, Query
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

@router.get("/", response_model=List[CollegeResponse])
def get_colleges(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    colleges = db.query(College).offset(skip).limit(limit).all()
    return colleges

@router.get("/{college_id}", response_model=CollegeResponse)
def get_college(
    college_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    college = db.query(College).filter(College.id == college_id).first()

    if not college:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="College not found"
        )

    return college

@router.post("/", response_model=CollegeResponse, status_code=201)
def create_college(
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
def update_college(
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
def delete_college(
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

    db.delete(college)
    db.commit()

    return None


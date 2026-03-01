"""
User management endpoints - Production Ready
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.logger import logger
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


# Helpers
def ensure_admin(user: User):
    if user.role != UserRole.ADMIN:
        raise ForbiddenError("Admin access required")


def sanitize_user(user: User) -> UserResponse:
    """Prevent exposing sensitive fields"""
    return UserResponse.model_validate(user)


# Get Current User Profile
@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return sanitize_user(current_user)


# Get User By ID (Admin Only)
@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise NotFoundError("User not found")

    return sanitize_user(user)

# List Users (Admin Only)

@router.get("/", response_model=List[UserResponse])
async def list_users(
    role: Optional[UserRole] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin(current_user)

    query = db.query(User)

    if role:
        query = query.filter(User.role == role)

    users = query.offset(skip).limit(limit).all()

    return [sanitize_user(user) for user in users]


# Update Own Profile
@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if update_data.full_name:
            if len(update_data.full_name.strip()) < 2:
                raise ValidationError("Full name too short")
            current_user.full_name = update_data.full_name.strip()

        db.commit()
        db.refresh(current_user)

        logger.info(f"User updated profile: {current_user.id}")

        return sanitize_user(current_user)

    except ValidationError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error updating profile: {e}")
        raise

# Deactivate User (Admin Only)

@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise NotFoundError("User not found")

    user.is_active = False

    db.commit()
    db.refresh(user)

    logger.warning(f"User deactivated: {user.id} by admin {current_user.id}")

    return sanitize_user(user)
from fastapi import APIRouter, Depends, status, File, UploadFile
import shutil
import uuid
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import ValidationError
from app.core.logger import logger
from app.models.user import User
from app.schemas.user import UserResponse, UserSelfUpdate

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Get the current user's full profile details (including emergency contacts, blood group, etc.)
    """
    return UserResponse.model_validate(current_user)


@router.post("/me", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_my_profile(
    profile_data: UserSelfUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Set up the user's profile for the first time after registration.
    """
    try:
        if profile_data.full_name is not None:
            if len(profile_data.full_name.strip()) < 2:
                raise ValidationError("Full name too short")
            current_user.full_name = profile_data.full_name.strip()
        
        if profile_data.phone is not None:
            current_user.phone = profile_data.phone
        if profile_data.blood_group is not None:
            current_user.blood_group = profile_data.blood_group
        if profile_data.emergency_contact_1 is not None:
            current_user.emergency_contact_1 = profile_data.emergency_contact_1
        if profile_data.emergency_contact_2 is not None:
            current_user.emergency_contact_2 = profile_data.emergency_contact_2
        if profile_data.profile_image is not None:
            current_user.profile_image = profile_data.profile_image
        
        # Social handles
        if profile_data.social_instagram is not None:
            current_user.social_instagram = profile_data.social_instagram
        if profile_data.social_linkedin is not None:
            current_user.social_linkedin = profile_data.social_linkedin
        if profile_data.social_github is not None:
            current_user.social_github = profile_data.social_github
            
        # Notification settings
        if profile_data.push_notifications is not None:
            current_user.push_notifications = profile_data.push_notifications
        if profile_data.location_access is not None:
            current_user.location_access = profile_data.location_access
        if profile_data.dark_mode is not None:
            current_user.dark_mode = profile_data.dark_mode
        if profile_data.preferred_language is not None:
            current_user.preferred_language = profile_data.preferred_language

        db.commit()
        db.refresh(current_user)

        logger.info(f"User created/initialized profile: {current_user.id}")

        return UserResponse.model_validate(current_user)

    except ValidationError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error creating profile: {e}")
        raise


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    update_data: UserSelfUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the current user's profile details.
    """
    try:
        if update_data.full_name is not None:
            if len(update_data.full_name.strip()) < 2:
                raise ValidationError("Full name too short")
            current_user.full_name = update_data.full_name.strip()
        
        if update_data.phone is not None:
            current_user.phone = update_data.phone
        if update_data.blood_group is not None:
            current_user.blood_group = update_data.blood_group
        if update_data.emergency_contact_1 is not None:
            current_user.emergency_contact_1 = update_data.emergency_contact_1
        if update_data.emergency_contact_2 is not None:
            current_user.emergency_contact_2 = update_data.emergency_contact_2
        if update_data.profile_image is not None:
            current_user.profile_image = update_data.profile_image

        # Social handles
        if update_data.social_instagram is not None:
            current_user.social_instagram = update_data.social_instagram
        if update_data.social_linkedin is not None:
            current_user.social_linkedin = update_data.social_linkedin
        if update_data.social_github is not None:
            current_user.social_github = update_data.social_github
            
        # Notification settings
        if update_data.push_notifications is not None:
            current_user.push_notifications = update_data.push_notifications
        if update_data.location_access is not None:
            current_user.location_access = update_data.location_access
        if update_data.dark_mode is not None:
            current_user.dark_mode = update_data.dark_mode
        if update_data.preferred_language is not None:
            current_user.preferred_language = update_data.preferred_language

        db.commit()
        db.refresh(current_user)

        logger.info(f"User updated profile: {current_user.id}")

        return UserResponse.model_validate(current_user)

    except ValidationError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error updating profile: {e}")
        raise

@router.post("/upload-profile-image", response_model=UserResponse)
async def upload_profile_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload and update the current user's profile image.
    """
    # Ensure directory exists
    upload_dir = "static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update DB URL
    # Assuming backend runs on localhost:8000
    # In production, use the actual domain from config
    image_url = f"/static/uploads/{unique_filename}"
    current_user.profile_image = image_url
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)

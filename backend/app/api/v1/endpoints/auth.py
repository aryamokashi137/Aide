import re
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.exceptions import (
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
    ValidationError,
)
from app.core.logger import logger
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    RefreshTokenRequest,
    RefreshTokenResponse,
)
from fastapi.security import OAuth2PasswordRequestForm 

router = APIRouter()

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128




# REGISTER
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Normalize email
        email = user_data.email.lower().strip()

        # Check if email already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise ConflictError("Email already registered")

        # Hash password
        hashed_password = get_password_hash(user_data.password)

        # Create user
        db_user = User(
            full_name=user_data.full_name.strip(),
            email=email,
            hashed_password=hashed_password,
            role=UserRole.USER,  # force default role
            is_active=True,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"User registered successfully: {db_user.id}")

        return UserResponse.model_validate(db_user)

    except ConflictError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during registration: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected registration error: {e}")
        raise

# LOGIN
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        email = form_data.username.lower().strip()

        user = db.query(User).filter(User.email == email).first()

        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for: {email}")
            raise UnauthorizedError("Incorrect email or password")

        if not user.is_active:
            raise ForbiddenError("User account is inactive")

        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
            },
            expires_delta=access_token_expires,
        )

        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )

        logger.info(f"User logged in successfully: {user.id}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    except (UnauthorizedError, ForbiddenError):
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise UnauthorizedError("Login failed")

# REFRESH TOKEN
@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        payload = verify_refresh_token(refresh_data.refresh_token)

        if not payload:
            raise UnauthorizedError("Invalid refresh token")

        user_id = int(payload.get("sub"))

        user = db.query(User).filter(User.id == user_id).first()

        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
            },
            expires_delta=access_token_expires,
        )

        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise UnauthorizedError("Token refresh failed")

# CURRENT USER
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
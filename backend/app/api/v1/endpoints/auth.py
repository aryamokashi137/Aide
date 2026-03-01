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

router = APIRouter()

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


# VALIDATION HELPERS
def validate_password(password: str) -> str:
    if not password:
        raise ValidationError("Password is required")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")

    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValidationError("Password too long")

    return password


def validate_email(email: str) -> str:
    if not email:
        raise ValidationError("Email is required")

    email = email.lower().strip()

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ValidationError("Invalid email format")

    return email


def validate_username(username: str) -> str:
    if not username:
        raise ValidationError("Username is required")

    username = username.strip()

    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters")

    if len(username) > 30:
        raise ValidationError("Username too long")

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        raise ValidationError("Username can only contain letters, numbers, and underscores")

    return username

# REGISTER
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        email = validate_email(user_data.email)
        username = validate_username(user_data.username)
        password = validate_password(user_data.password)

        # Check uniqueness
        existing = (
            db.query(User)
            .filter((User.email == email) | (User.username == username))
            .first()
        )

        if existing:
            if existing.email == email:
                raise ConflictError("Email already registered")
            raise ConflictError("Username already taken")

        db_user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            full_name=user_data.full_name.strip() if user_data.full_name else None,
            organization_id=user_data.organization_id,
            role=UserRole.USER,
            is_active=True,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"User registered: {db_user.id}")

        return db_user

    except (ValidationError, ConflictError):
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error during registration: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during registration: {e}")
        raise


# LOGIN
@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    try:
        username = credentials.username.strip()

        user = db.query(User).filter(User.username == username).first()

        # Timing attack safe check
        if not user or not verify_password(credentials.password, user.hashed_password):
            logger.warning(f"Failed login attempt for: {username}")
            raise UnauthorizedError("Incorrect username or password")

        if not user.is_active:
            raise ForbiddenError("User account is inactive")

        # Organization auth policy check
        if user.organization_id:
            org = db.query(Organization).filter(
                Organization.id == user.organization_id
            ).first()

            if org and str(getattr(org, "auth_policy", "")).upper() == "SSO_ONLY":
                raise ForbiddenError(
                    "This organization requires SSO login."
                )

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

        logger.info(f"User logged in: {user.id}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
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
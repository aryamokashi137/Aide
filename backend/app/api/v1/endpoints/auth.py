import re
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta, datetime
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
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from fastapi.security import OAuth2PasswordRequestForm
import uuid
import secrets
from app.services.email import send_verification_email, send_password_reset_email
from app.core.redis import blacklist_token, set_otp, get_otp, delete_otp

router = APIRouter()

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

from fastapi_limiter.depends import RateLimiter
from app.api.v1.endpoints.deps import oauth2_scheme

# REGISTER
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
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

        # Create user with verification token
        verification_token = str(uuid.uuid4())
        db_user = User(
            full_name=user_data.full_name.strip(),
            email=email,
            hashed_password=hashed_password,
            role=UserRole.USER,
            is_active=True,
            is_verified=False,
            verification_token=verification_token
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Send verification email
        send_verification_email(email, verification_token)

        logger.info(f"User registered successfully: {db_user.id}. Verification email sent.")

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
@router.post("/login", response_model=Token, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
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

        if not user.is_verified:
            raise ForbiddenError("Please verify your email address before logging in")

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

# LOGOUT
@router.post("/logout", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """
    Logout the current user by blacklisting their access token in Redis.
    """
    # Blacklist for the duration of its expiry (30 mins by default)
    await blacklist_token(token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    logger.info(f"User logged out and token blacklisted: {current_user.id}")
    return {"message": "Successfully logged out"}

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

# EMAIL VERIFICATION
@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise ValidationError("Invalid or expired verification token")
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    
    return {"message": "Email verified successfully. You can now log in."}

# FORGOT PASSWORD
@router.post("/forgot-password", dependencies=[Depends(RateLimiter(times=3, seconds=60))])
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = request.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()
    if user:
        # Generate 6-digit OTP
        otp_code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        
        # Store in Redis for 10 minutes
        await set_otp(email, otp_code, expire_seconds=600)
        
        # Send password reset email (using OTP instead of link if desired, or just code)
        send_password_reset_email(user.email, otp_code)
        logger.info(f"OTP sent to {email} for password reset.")
    
    # Always return success to prevent email enumeration
    return {"message": "If an account exists with that email, a verification code has been sent."}

# RESET PASSWORD
@router.post("/reset-password", dependencies=[Depends(RateLimiter(times=3, seconds=60))])
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    # Verify OTP from Redis
    email = request.email.lower().strip() # Added email to request schema? I should check
    stored_otp = await get_otp(email)
    
    if not stored_otp or stored_otp != request.token:
        raise ValidationError("Invalid or expired reset code")
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise ValidationError("Invalid or expired reset token")
    
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    # Delete OTP after successful reset
    await delete_otp(email)
    
    return {"message": "Password reset successfully. You can now log in."}
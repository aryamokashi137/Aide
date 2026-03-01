from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a short‑lived access token. Optional expires_delta overrides the
    default expiration period."""
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_password_hash(password: str):
    # alias used throughout the codebase for clarity
    return hash_password(password)


def create_refresh_token(data: dict):
    """Generate a long‑lived JWT for refreshing access tokens."""
    from app.core.config import settings

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_refresh_token(token: str) -> dict | None:
    """Validate a refresh token, returning payload or None if invalid."""
    from jose import JWTError

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


from app.core.redis import is_token_blacklisted

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    # Check if token is blacklisted
    if await is_token_blacklisted(token):
        logger.warning(f"Attempt to use blacklisted token: {token[:10]}...")
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


def require_roles(*roles):
    """Dependency factory that accepts role names or UserRole enums.

    Normalizes allowed roles to their lowercase values so callers can pass
    either strings like 'admin'/'ADMIN' or `UserRole.ADMIN`.
    """
    # allow callers to pass either multiple args, or a single iterable (list/tuple/set)
    if len(roles) == 1 and isinstance(roles[0], (list, tuple, set)):
        roles_iter = roles[0]
    else:
        roles_iter = roles

    # normalize allowed roles to lower-case role values
    allowed = set()
    for r in roles_iter:
        if isinstance(r, UserRole):
            allowed.add(r.value.lower())
        else:
            allowed.add(str(r).lower())

    def role_checker(current_user: User = Depends(get_current_user)):
        # get current user's role as lower-case string
        current_role = (
            current_user.role.value.lower()
            if isinstance(current_user.role, UserRole)
            else str(current_user.role).lower()
        )

        if current_role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user

    return role_checker
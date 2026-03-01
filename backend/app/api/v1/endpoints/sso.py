"""
Google SSO (OIDC) — Authorization Code Flow (Backend Controlled)
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import httpx
from authlib.jose import jwt as authlib_jwt
from authlib.jose.rfc7517 import JsonWebKey

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.core.logger import logger
from app.models.user import User, UserRole

router = APIRouter(prefix="/auth/google", tags=["Google SSO"])

GOOGLE_ISSUER = "https://accounts.google.com"
STATE_TTL = 600


def _make_state(nonce: str) -> str:
    payload = json.dumps({"nonce": nonce, "ts": int(time.time())})
    payload_b64 = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
    sig = hmac.new(
        settings.SECRET_KEY.encode(),
        payload_b64.encode(),
        hashlib.sha256,
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{payload_b64}.{sig_b64}"


def _verify_state(state: str) -> dict | None:
    try:
        payload_b64, sig_b64 = state.split(".")
        payload = json.loads(
            base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4)).decode()
        )
        ts = payload.get("ts")
        if not ts or abs(time.time() - ts) > STATE_TTL:
            return None
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256,
        ).digest()
        sig = base64.urlsafe_b64decode(sig_b64 + "=" * (-len(sig_b64) % 4))
        if not hmac.compare_digest(sig, expected_sig):
            return None
        return payload
    except Exception:
        return None


async def _fetch_metadata():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{GOOGLE_ISSUER}/.well-known/openid-configuration")
        r.raise_for_status()
        return r.json()


async def _fetch_jwks(jwks_uri: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(jwks_uri)
        r.raise_for_status()
        return r.json()


def _verify_id_token(id_token: str, nonce: str, client_id: str, jwks_dict: dict):
    key_set = JsonWebKey.import_key_set(jwks_dict)
    claims = authlib_jwt.decode(
        id_token,
        key_set,
        claims_params={"iss": GOOGLE_ISSUER, "aud": client_id},
    )
    claims.validate()
    if claims.get("nonce") != nonce:
        raise ValueError("Invalid nonce")
    return claims


async def _exchange_code(code: str, redirect_uri: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        r.raise_for_status()
        return r.json()


def _provision_user(db: Session, claims: dict):
    email = (claims.get("email") or "").lower().strip()
    if not email:
        raise ValueError("Email not provided by Google")

    user = db.query(User).filter(User.email == email).first()
    if user:
        if not user.is_active:
            raise ValueError("User inactive")
        return user

    username_base = email.split("@")[0][:30]
    username = username_base
    n = 0
    while db.query(User).filter(User.username == username).first():
        n += 1
        username = f"{username_base}{n}"[:30]

    user = User(
        email=email,
        username=username,
        full_name=claims.get("name"),
        hashed_password=get_password_hash(secrets.token_urlsafe(32)),
        role=UserRole.STUDENT,
        is_active=True,
        auth_method="SSO",
        idp_issuer=GOOGLE_ISSUER,
        idp_sub=claims.get("sub"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/login")
async def google_login():
    metadata = await _fetch_metadata()
    auth_endpoint = metadata["authorization_endpoint"]

    nonce = secrets.token_urlsafe(32)
    state = _make_state(nonce)

    params = {
        "response_type": "code",
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "state": state,
        "nonce": nonce,
        "access_type": "offline",
        "prompt": "consent",
    }

    return RedirectResponse(f"{auth_endpoint}?{urlencode(params)}")


@router.get("/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    frontend_url = settings.SSO_FRONTEND_SUCCESS_URL

    if error:
        return RedirectResponse(f"{frontend_url}?error={error}")

    if not code or not state:
        return RedirectResponse(f"{frontend_url}?error=missing_code_or_state")

    state_payload = _verify_state(state)
    if not state_payload:
        return RedirectResponse(f"{frontend_url}?error=invalid_state")

    nonce = state_payload.get("nonce")

    try:
        metadata = await _fetch_metadata()
        token_response = await _exchange_code(code, settings.GOOGLE_REDIRECT_URI)

        id_token = token_response.get("id_token")
        if not id_token:
            return RedirectResponse(f"{frontend_url}?error=no_id_token")

        jwks = await _fetch_jwks(metadata["jwks_uri"])
        claims = _verify_id_token(
            id_token, nonce, settings.GOOGLE_CLIENT_ID, jwks
        )

        user = _provision_user(db, claims)

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        fragment = urlencode(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        )

        return RedirectResponse(f"{frontend_url}#{fragment}")

    except Exception as e:
        logger.exception(f"Google SSO error: {e}")
        return RedirectResponse(f"{frontend_url}?error=server_error")
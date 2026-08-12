import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def hash_otp(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def generate_challenge_id() -> str:
    return secrets.token_urlsafe(24)


def create_access_token(patient_id: str) -> str:
    settings = get_settings()
    now = utcnow()
    payload: dict[str, Any] = {
        "sub": patient_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão expirada.",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        ) from exc

    if payload.get("type") != "access" or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        )

    return payload


def get_current_patient_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação obrigatória.",
        )

    payload = decode_access_token(credentials.credentials)
    return str(payload["sub"])

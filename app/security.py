import hashlib
import secrets
import string
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings
from app.database import get_supabase


bearer_scheme = HTTPBearer(auto_error=False)

ALPHANUMERIC = string.ascii_letters + string.digits


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_alphanumeric_token(length: int) -> str:
    """
    Gera um valor aleatório contendo apenas:
    A-Z, a-z e 0-9.
    """
    return "".join(
        secrets.choice(ALPHANUMERIC)
        for _ in range(length)
    )


def generate_challenge_id() -> str:
    return generate_alphanumeric_token(32)


def generate_session_id() -> str:
    return generate_alphanumeric_token(32)


def generate_access_token() -> str:
    return generate_alphanumeric_token(64)


def hash_otp(code: str) -> str:
    return hashlib.sha256(
        code.encode("utf-8")
    ).hexdigest()


def hash_access_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def get_current_patient_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
) -> str:
    """
    Valida o access_token e a sessão.

    A sessão é válida quando:
    - o token existe;
    - a sessão não foi revogada;
    - não ultrapassou 8 horas de duração máxima;
    - não ficou mais de 2 horas sem atividade.

    A cada chamada válida, last_activity_at é atualizado.
    """

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação obrigatória.",
        )

    settings = get_settings()
    supabase = get_supabase()

    access_token = credentials.credentials
    token_hash = hash_access_token(access_token)

    response = (
        supabase.table("sessions")
        .select("*")
        .eq("token_hash", token_hash)
        .limit(1)
        .execute()
    )

    sessions = response.data or []

    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        )

    session = sessions[0]

    if session.get("revoked"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão encerrada.",
        )

    now = utcnow()

    absolute_expires_at = parse_datetime(
        session["absolute_expires_at"]
    )

    # Duração máxima da sessão: 8 horas
    if now >= absolute_expires_at:
        (
            supabase.table("sessions")
            .update({"revoked": True})
            .eq("id", session["id"])
            .execute()
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão expirada.",
        )

    last_activity_at = parse_datetime(
        session["last_activity_at"]
    )

    idle_seconds = (
        now - last_activity_at
    ).total_seconds()

    idle_limit_seconds = (
        settings.session_idle_timeout_minutes * 60
    )

    # Tempo máximo sem interação: 2 horas
    if idle_seconds >= idle_limit_seconds:
        (
            supabase.table("sessions")
            .update({"revoked": True})
            .eq("id", session["id"])
            .execute()
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão expirada por inatividade.",
        )

    # Houve atividade válida:
    # renova o horário da última interação.
    (
        supabase.table("sessions")
        .update(
            {
                "last_activity_at": now.isoformat()
            }
        )
        .eq("id", session["id"])
        .execute()
    )

    return str(session["patient_id"])
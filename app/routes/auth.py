from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.database import get_supabase
from app.schemas.auth import (
    OtpRequestIn,
    OtpRequestOut,
    OtpVerifyIn,
    OtpVerifyOut,
)
from app.security import (
    generate_access_token,
    generate_challenge_id,
    generate_session_id,
    hash_access_token,
    hash_otp,
    utcnow,
)
from app.utils import phone_last_digits


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/otp/request",
    response_model=OtpRequestOut,
)
def request_otp(
    payload: OtpRequestIn,
) -> OtpRequestOut:

    settings = get_settings()
    supabase = get_supabase()

    response = (
        supabase.table("patients")
        .select("id,phone")
        .eq("id", payload.patient_id)
        .limit(1)
        .execute()
    )

    rows = response.data or []

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Paciente não encontrado.",
        )

    patient = rows[0]

    challenge_id = generate_challenge_id()

    expires_at = utcnow() + timedelta(
        minutes=settings.otp_expire_minutes
    )

    supabase.table(
        "auth_challenges"
    ).insert(
        {
            "id": challenge_id,
            "patient_id": payload.patient_id,
            "code_hash": hash_otp(
                settings.dev_otp_code
            ),
            "expires_at": expires_at.isoformat(),
            "used": False,
        }
    ).execute()

    # TODO:
    # Integrar SMS/WhatsApp real em produção.

    return OtpRequestOut(
        challenge_id=challenge_id,
        phone_last_digits=phone_last_digits(
            patient.get("phone")
        ),
        expires_in=(
            settings.otp_expire_minutes * 60
        ),
        dev_code=(
            settings.dev_otp_code
            if settings.return_dev_otp
            else None
        ),
    )


@router.post(
    "/otp/verify",
    response_model=OtpVerifyOut,
)
def verify_otp(
    payload: OtpVerifyIn,
) -> OtpVerifyOut:

    settings = get_settings()
    supabase = get_supabase()

    response = (
        supabase.table("auth_challenges")
        .select("*")
        .eq("id", payload.challenge_id)
        .limit(1)
        .execute()
    )

    rows = response.data or []

    if not rows:
        return OtpVerifyOut(
            success=False,
            authenticated=False,
            error="CHALLENGE_NOT_FOUND",
            message=(
                "Código de autenticação "
                "não encontrado."
            ),
        )

    challenge = rows[0]

    if challenge.get("used"):
        return OtpVerifyOut(
            success=False,
            authenticated=False,
            error="OTP_ALREADY_USED",
            message=(
                "Esse código já foi utilizado."
            ),
        )

    expires_at = challenge.get(
        "expires_at"
    )

    if expires_at:
        parsed_expires_at = (
            datetime.fromisoformat(
                expires_at.replace(
                    "Z",
                    "+00:00",
                )
            )
        )

        if utcnow() > parsed_expires_at:
            return OtpVerifyOut(
                success=False,
                authenticated=False,
                error="OTP_EXPIRED",
                message=(
                    "O código expirou. "
                    "Solicite um novo código."
                ),
            )

    if (
        hash_otp(payload.code)
        != challenge.get("code_hash")
    ):
        return OtpVerifyOut(
            success=False,
            authenticated=False,
            error="INVALID_OTP",
            message="Código incorreto.",
        )

    # Marca o OTP como utilizado
    (
        supabase.table("auth_challenges")
        .update({"used": True})
        .eq(
            "id",
            payload.challenge_id,
        )
        .execute()
    )

    # Cria a nova sessão
    now = utcnow()

    session_id = generate_session_id()
    access_token = generate_access_token()

    absolute_expires_at = (
        now
        + timedelta(
            minutes=(
                settings
                .session_max_lifetime_minutes
            )
        )
    )

    (
        supabase.table("sessions")
        .insert(
            {
                "id": session_id,
                "patient_id": (
                    challenge["patient_id"]
                ),
                "token_hash": (
                    hash_access_token(
                        access_token
                    )
                ),
                "created_at": (
                    now.isoformat()
                ),
                "last_activity_at": (
                    now.isoformat()
                ),
                "absolute_expires_at": (
                    absolute_expires_at
                    .isoformat()
                ),
                "revoked": False,
            }
        )
        .execute()
    )

    return OtpVerifyOut(
        success=True,
        authenticated=True,
        session_id=session_id,
        access_token=access_token,
        token_type="bearer",
        idle_timeout=(
            settings
            .session_idle_timeout_minutes
            * 60
        ),
        max_session_lifetime=(
            settings
            .session_max_lifetime_minutes
            * 60
        ),
    )
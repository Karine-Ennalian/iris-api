from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_supabase
from app.schemas.patient import (
    HealthUnitSummary,
    PatientLookupIn,
    PatientLookupOut,
    PatientMeOut,
    PatientPublic,
)
from app.security import get_current_patient_id
from app.utils import first_name, mask_cpf, phone_last_digits, validate_cns_format

router = APIRouter(prefix="/patients", tags=["Patients"])


def _public_patient(row: dict, health_unit: dict | None = None) -> PatientPublic:
    return PatientPublic(
        id=str(row["id"]),
        cns=row["cns"],
        name=row["name"],
        first_name=first_name(row.get("name")),
        cpf_masked=mask_cpf(row.get("cpf")),
        birth_date=row.get("birth_date"),
        phone_last_digits=phone_last_digits(row.get("phone")),
        health_unit=(
            HealthUnitSummary(id=str(health_unit["id"]), name=health_unit.get("name"))
            if health_unit
            else None
        ),
    )


@router.post("/lookup", response_model=PatientLookupOut)
def lookup_patient(payload: PatientLookupIn) -> PatientLookupOut:
    try:
        cns = validate_cns_format(payload.cns)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    supabase = get_supabase()
    response = supabase.table("patients").select("*").eq("cns", cns).limit(1).execute()
    rows = response.data or []

    if not rows:
        return PatientLookupOut(
            found=False,
            error="PATIENT_NOT_FOUND",
            message="Nenhum paciente foi encontrado para o CNS informado.",
        )

    patient = rows[0]
    unit = None
    if patient.get("health_unit_id"):
        unit_response = (
            supabase.table("health_units")
            .select("id,name")
            .eq("id", patient["health_unit_id"])
            .limit(1)
            .execute()
        )
        if unit_response.data:
            unit = unit_response.data[0]

    return PatientLookupOut(found=True, patient=_public_patient(patient, unit))


@router.get("/me", response_model=PatientMeOut)
def get_me(patient_id: str = Depends(get_current_patient_id)) -> PatientMeOut:
    supabase = get_supabase()
    response = supabase.table("patients").select("*").eq("id", patient_id).limit(1).execute()
    rows = response.data or []

    if not rows:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    row = rows[0]
    unit = None
    if row.get("health_unit_id"):
        unit_response = (
            supabase.table("health_units")
            .select("id,name")
            .eq("id", row["health_unit_id"])
            .limit(1)
            .execute()
        )
        if unit_response.data:
            unit = unit_response.data[0]

    public = _public_patient(row, unit)
    return PatientMeOut(
        **public.model_dump(),
        email=row.get("email"),
        address=row.get("address"),
    )

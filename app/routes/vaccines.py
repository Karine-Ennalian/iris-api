from fastapi import APIRouter, Depends

from app.database import get_supabase
from app.schemas.vaccine import VaccineOut
from app.security import get_current_patient_id

router = APIRouter(prefix="/vaccines", tags=["Vaccines"])


@router.get("", response_model=list[VaccineOut])
def list_vaccines(patient_id: str = Depends(get_current_patient_id)) -> list[VaccineOut]:
    supabase = get_supabase()
    response = supabase.table("vaccines").select("*").eq("patient_id", patient_id).execute()
    return [VaccineOut(**row) for row in (response.data or [])]


@router.get("/pending", response_model=list[VaccineOut])
def list_pending_vaccines(patient_id: str = Depends(get_current_patient_id)) -> list[VaccineOut]:
    supabase = get_supabase()
    response = (
        supabase.table("vaccines")
        .select("*")
        .eq("patient_id", patient_id)
        .eq("status", "pending")
        .execute()
    )
    return [VaccineOut(**row) for row in (response.data or [])]

from fastapi import APIRouter, Depends

from app.database import get_supabase
from app.security import get_current_patient_id

router = APIRouter(prefix="/history", tags=["History"])


@router.get("")
def get_history(patient_id: str = Depends(get_current_patient_id)) -> dict:
    supabase = get_supabase()

    appointments = (
        supabase.table("appointments")
        .select("*")
        .eq("patient_id", patient_id)
        .order("appointment_date", desc=True)
        .execute()
        .data
        or []
    )
    exams = (
        supabase.table("exams")
        .select("*")
        .eq("patient_id", patient_id)
        .order("request_date", desc=True)
        .execute()
        .data
        or []
    )
    vaccines = supabase.table("vaccines").select("*").eq("patient_id", patient_id).execute().data or []

    return {
        "patient_id": patient_id,
        "appointments": appointments,
        "exams": exams,
        "vaccines": vaccines,
    }

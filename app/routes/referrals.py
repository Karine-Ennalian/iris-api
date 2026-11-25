from fastapi import APIRouter, Depends
from app.database import get_supabase
from app.schemas.referral import ReferralOut
from app.security import get_current_patient_id


router = APIRouter(
    prefix="/referrals",
    tags=["Referrals"]
)

STATUS_LABELS = {
    "pending": "Aguardando agendamento",
    "scheduled": "Agendado",
    "completed": "Concluído",
    "cancelled": "Cancelado",
}


@router.get("", response_model=list[ReferralOut])
def list_referrals(
    patient_id: str = Depends(get_current_patient_id)
) -> list[ReferralOut]:

    response = (
        get_supabase()
        .table("referrals")
        .select(
            "id,specialty,reason,request_date,"
            "scheduled_date,status,health_unit_name"
        )
        .eq("patient_id", patient_id)
        .order("request_date", desc=True)
        .order("id")
        .execute()
    )

    return [
        ReferralOut(
            **row,
            status_label=STATUS_LABELS.get(
                row["status"],
                "Não reconhecido"
            )
        )
        for row in (response.data or [])
    ]
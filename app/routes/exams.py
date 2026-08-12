from fastapi import APIRouter, Depends, HTTPException

from app.database import get_supabase
from app.schemas.exam import ExamOut, ExamResultOut
from app.security import get_current_patient_id

router = APIRouter(prefix="/exams", tags=["Exams"])


@router.get("", response_model=list[ExamOut])
def list_exams(patient_id: str = Depends(get_current_patient_id)) -> list[ExamOut]:
    supabase = get_supabase()
    response = (
        supabase.table("exams")
        .select("*")
        .eq("patient_id", patient_id)
        .order("request_date", desc=True)
        .execute()
    )
    return [ExamOut(**row) for row in (response.data or [])]


@router.get("/{exam_id}/result", response_model=ExamResultOut)
def get_exam_result(
    exam_id: str,
    patient_id: str = Depends(get_current_patient_id),
) -> ExamResultOut:
    supabase = get_supabase()
    response = (
        supabase.table("exams")
        .select("*")
        .eq("id", exam_id)
        .eq("patient_id", patient_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Exame não encontrado.")

    row = response.data[0]
    return ExamResultOut(
        id=str(row["id"]),
        exam_type=row["exam_type"],
        status=row["status"],
        result_text=row.get("result_text"),
        result_url=row.get("result_url"),
    )

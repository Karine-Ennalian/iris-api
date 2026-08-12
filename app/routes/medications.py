from fastapi import APIRouter, Depends, Query

from app.database import get_supabase
from app.schemas.medication import MedicationOut, MedicationStockOut
from app.security import get_current_patient_id

router = APIRouter(prefix="/medications", tags=["Medications"])


@router.get("/search", response_model=list[MedicationOut])
def search_medications(
    name: str = Query(min_length=2),
    _: str = Depends(get_current_patient_id),
) -> list[MedicationOut]:
    supabase = get_supabase()
    response = supabase.table("medications").select("*").ilike("name", f"%{name}%").execute()
    return [MedicationOut(**row) for row in (response.data or [])]


@router.get("/{medication_id}/availability", response_model=list[MedicationStockOut])
def medication_availability(
    medication_id: str,
    _: str = Depends(get_current_patient_id),
) -> list[MedicationStockOut]:
    supabase = get_supabase()

    med_response = supabase.table("medications").select("*").eq("id", medication_id).limit(1).execute()
    if not med_response.data:
        return []
    medication = med_response.data[0]

    stock_response = (
        supabase.table("medication_stock")
        .select("*")
        .eq("medication_id", medication_id)
        .gt("quantity", 0)
        .execute()
    )

    result: list[MedicationStockOut] = []
    for row in stock_response.data or []:
        unit_response = (
            supabase.table("health_units")
            .select("name")
            .eq("id", row["health_unit_id"])
            .limit(1)
            .execute()
        )
        unit_name = unit_response.data[0]["name"] if unit_response.data else "Unidade"
        quantity = int(row["quantity"])
        stock_status = "low_stock" if quantity <= 10 else "available"
        result.append(
            MedicationStockOut(
                medication_id=str(medication["id"]),
                medication_name=medication["name"],
                health_unit_id=str(row["health_unit_id"]),
                health_unit_name=unit_name,
                quantity=quantity,
                status=stock_status,
            )
        )
    return result

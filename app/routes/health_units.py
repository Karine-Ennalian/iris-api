from fastapi import APIRouter, Depends, Query

from app.database import get_supabase
from app.schemas.health_unit import HealthUnitOut
from app.security import get_current_patient_id

router = APIRouter(prefix="/health-units", tags=["Health Units"])


@router.get("", response_model=list[HealthUnitOut])
def list_health_units(
    neighborhood: str | None = None,
    unit_type: str | None = Query(default=None, alias="type"),
    _: str = Depends(get_current_patient_id),
) -> list[HealthUnitOut]:
    supabase = get_supabase()
    query = supabase.table("health_units").select("*")
    if neighborhood:
        query = query.ilike("neighborhood", f"%{neighborhood}%")
    if unit_type:
        query = query.eq("type", unit_type)
    response = query.order("name").execute()
    return [HealthUnitOut(**row) for row in (response.data or [])]

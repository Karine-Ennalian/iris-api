from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import get_supabase
from app.schemas.appointment import (
    AppointmentCreateIn,
    AppointmentOut,
    AppointmentSlotOut,
    AppointmentUpdateIn,
)
from app.security import get_current_patient_id


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


def _appointment_out(
    row: dict,
    unit_name: str | None = None,
) -> AppointmentOut:
    return AppointmentOut(
        id=str(row["id"]),
        specialty=row["specialty"],
        professional_name=row.get("professional_name"),
        health_unit_id=str(row["health_unit_id"]),
        health_unit_name=unit_name,
        appointment_date=row["appointment_date"],
        appointment_time=row["appointment_time"],
        status=row["status"],
    )


def _unit_name(
    unit_id: str,
) -> str | None:
    supabase = get_supabase()

    response = (
        supabase.table("health_units")
        .select("name")
        .eq("id", unit_id)
        .limit(1)
        .execute()
    )

    return (
        response.data[0]["name"]
        if response.data
        else None
    )


@router.get(
    "",
    response_model=list[AppointmentOut],
)
def list_appointments(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    patient_id: str = Depends(
        get_current_patient_id
    ),
) -> list[AppointmentOut]:

    supabase = get_supabase()

    query = (
        supabase.table("appointments")
        .select("*")
        .eq("patient_id", patient_id)
    )

    if status_filter:
        query = query.eq(
            "status",
            status_filter,
        )

    response = (
        query
        .order("appointment_date")
        .order("appointment_time")
        .execute()
    )

    return [
        _appointment_out(
            row,
            _unit_name(
                str(row["health_unit_id"])
            ),
        )
        for row in (response.data or [])
    ]


@router.get(
    "/availability",
    response_model=list[AppointmentSlotOut],
)
def list_available_slots(
    specialty: str | None = None,
    health_unit_id: str | None = None,
    _: str = Depends(
        get_current_patient_id
    ),
) -> list[AppointmentSlotOut]:

    supabase = get_supabase()

    query = (
        supabase.table("appointment_slots")
        .select("*")
        .eq("available", True)
    )

    if specialty:
        query = query.ilike(
            "specialty",
            specialty,
        )

    if health_unit_id:
        query = query.eq(
            "health_unit_id",
            health_unit_id,
        )

    response = (
        query
        .order("appointment_date")
        .order("appointment_time")
        .execute()
    )

    result = []

    for row in response.data or []:
        result.append(
            AppointmentSlotOut(
                id=str(row["id"]),
                specialty=row["specialty"],
                professional_name=row.get(
                    "professional_name"
                ),
                health_unit_id=str(
                    row["health_unit_id"]
                ),
                health_unit_name=_unit_name(
                    str(row["health_unit_id"])
                ),
                appointment_date=row[
                    "appointment_date"
                ],
                appointment_time=row[
                    "appointment_time"
                ],
            )
        )

    return result


@router.post(
    "",
    response_model=AppointmentOut,
    status_code=201,
)
def create_appointment(
    payload: AppointmentCreateIn,
    patient_id: str = Depends(
        get_current_patient_id
    ),
) -> AppointmentOut:

    supabase = get_supabase()

    slot_response = (
        supabase.table("appointment_slots")
        .select("*")
        .eq("id", payload.slot_id)
        .eq("available", True)
        .limit(1)
        .execute()
    )

    if not slot_response.data:
        raise HTTPException(
            status_code=409,
            detail="Horário indisponível.",
        )

    slot = slot_response.data[0]

    insert_response = (
        supabase.table("appointments")
        .insert(
            {
                "patient_id": patient_id,
                "specialty": slot[
                    "specialty"
                ],
                "professional_name": (
                    slot.get(
                        "professional_name"
                    )
                ),
                "health_unit_id": slot[
                    "health_unit_id"
                ],
                "appointment_date": slot[
                    "appointment_date"
                ],
                "appointment_time": slot[
                    "appointment_time"
                ],
                "status": "scheduled",
            }
        )
        .execute()
    )

    appointment = insert_response.data[0]

    (
        supabase.table("appointment_slots")
        .update(
            {
                "available": False
            }
        )
        .eq(
            "id",
            payload.slot_id,
        )
        .execute()
    )

    return _appointment_out(
        appointment,
        _unit_name(
            str(slot["health_unit_id"])
        ),
    )


@router.patch(
    "/{appointment_id}",
    response_model=AppointmentOut,
)
def reschedule_appointment(
    appointment_id: str,
    payload: AppointmentUpdateIn,
    patient_id: str = Depends(
        get_current_patient_id
    ),
) -> AppointmentOut:

    supabase = get_supabase()

    appointment_response = (
        supabase.table("appointments")
        .select("*")
        .eq(
            "id",
            appointment_id,
        )
        .eq(
            "patient_id",
            patient_id,
        )
        .limit(1)
        .execute()
    )

    if not appointment_response.data:
        raise HTTPException(
            status_code=404,
            detail="Consulta não encontrada.",
        )

    old_appointment = (
        appointment_response.data[0]
    )

    if (
        old_appointment.get("status")
        != "scheduled"
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Essa consulta não pode "
                "ser remarcada."
            ),
        )

    slot_response = (
        supabase.table("appointment_slots")
        .select("*")
        .eq(
            "id",
            payload.new_slot_id,
        )
        .eq(
            "available",
            True,
        )
        .limit(1)
        .execute()
    )

    if not slot_response.data:
        raise HTTPException(
            status_code=409,
            detail=(
                "Novo horário indisponível."
            ),
        )

    slot = slot_response.data[0]

    update_response = (
        supabase.table("appointments")
        .update(
            {
                "specialty": slot[
                    "specialty"
                ],
                "professional_name": (
                    slot.get(
                        "professional_name"
                    )
                ),
                "health_unit_id": slot[
                    "health_unit_id"
                ],
                "appointment_date": slot[
                    "appointment_date"
                ],
                "appointment_time": slot[
                    "appointment_time"
                ],
            }
        )
        .eq(
            "id",
            appointment_id,
        )
        .execute()
    )

    (
        supabase.table("appointment_slots")
        .update(
            {
                "available": False
            }
        )
        .eq(
            "id",
            payload.new_slot_id,
        )
        .execute()
    )

    return _appointment_out(
        update_response.data[0],
        _unit_name(
            str(slot["health_unit_id"])
        ),
    )


@router.delete(
    "/{appointment_id}"
)
def cancel_appointment(
    appointment_id: str,
    patient_id: str = Depends(
        get_current_patient_id
    ),
) -> dict:

    supabase = get_supabase()

    response = (
        supabase.table("appointments")
        .select("id,status")
        .eq(
            "id",
            appointment_id,
        )
        .eq(
            "patient_id",
            patient_id,
        )
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Consulta não encontrada.",
        )

    if (
        response.data[0]["status"]
        == "cancelled"
    ):
        return {
            "success": True,
            "status": "cancelled",
            "message": (
                "A consulta já estava "
                "cancelada."
            ),
        }

    (
        supabase.table("appointments")
        .update(
            {
                "status": "cancelled"
            }
        )
        .eq(
            "id",
            appointment_id,
        )
        .execute()
    )

    return {
        "success": True,
        "status": "cancelled",
        "message": (
            "Consulta cancelada com sucesso."
        ),
    }
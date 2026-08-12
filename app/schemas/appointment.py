from datetime import date, time
from pydantic import BaseModel


class AppointmentOut(BaseModel):
    id: str
    specialty: str
    professional_name: str | None = None
    health_unit_id: str
    health_unit_name: str | None = None
    appointment_date: date
    appointment_time: time
    status: str


class AppointmentCreateIn(BaseModel):
    slot_id: str


class AppointmentUpdateIn(BaseModel):
    new_slot_id: str


class AppointmentSlotOut(BaseModel):
    id: str
    specialty: str
    professional_name: str | None = None
    health_unit_id: str
    health_unit_name: str | None = None
    appointment_date: date
    appointment_time: time

from datetime import date
from pydantic import BaseModel


class VaccineOut(BaseModel):
    id: str
    vaccine_name: str
    dose: str
    application_date: date | None = None
    status: str
    health_unit_name: str | None = None

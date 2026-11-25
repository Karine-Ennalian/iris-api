from datetime import date
from pydantic import BaseModel


class ReferralOut(BaseModel):
    id: str
    specialty: str
    reason: str
    request_date: date
    scheduled_date: date | None = None
    status: str
    status_label: str
    health_unit_name: str | None = None
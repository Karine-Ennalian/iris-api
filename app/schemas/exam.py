from datetime import date
from pydantic import BaseModel


class ExamOut(BaseModel):
    id: str
    exam_type: str
    request_date: date
    scheduled_date: date | None = None
    status: str
    health_unit_name: str | None = None
    preparation: str | None = None


class ExamResultOut(BaseModel):
    id: str
    exam_type: str
    status: str
    result_text: str | None = None
    result_url: str | None = None

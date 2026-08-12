from datetime import date
from pydantic import BaseModel, Field


class PatientLookupIn(BaseModel):
    cns: str = Field(min_length=1)


class HealthUnitSummary(BaseModel):
    id: str | None = None
    name: str | None = None


class PatientPublic(BaseModel):
    id: str
    cns: str
    name: str
    first_name: str | None = None
    cpf_masked: str | None = None
    birth_date: date | None = None
    phone_last_digits: str | None = None
    health_unit: HealthUnitSummary | None = None


class PatientLookupOut(BaseModel):
    success: bool = True
    found: bool
    patient: PatientPublic | None = None
    error: str | None = None
    message: str | None = None


class PatientMeOut(PatientPublic):
    email: str | None = None
    address: str | None = None

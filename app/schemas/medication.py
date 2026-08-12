from pydantic import BaseModel


class MedicationOut(BaseModel):
    id: str
    name: str
    dosage: str | None = None
    presentation: str | None = None


class MedicationStockOut(BaseModel):
    medication_id: str
    medication_name: str
    health_unit_id: str
    health_unit_name: str
    quantity: int
    status: str

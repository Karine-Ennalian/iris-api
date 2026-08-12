from pydantic import BaseModel


class HealthUnitOut(BaseModel):
    id: str
    name: str
    type: str
    address: str | None = None
    neighborhood: str | None = None
    phone: str | None = None
    latitude: float | None = None
    longitude: float | None = None

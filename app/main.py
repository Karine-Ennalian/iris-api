from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import (
    appointments,
    auth,
    exams,
    health,
    health_units,
    history,
    medications,
    patients,
    vaccines,
    referrals,
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API acadêmica/mock para a Íris, assistente virtual de saúde. "
        "Utiliza apenas dados fictícios para simular integrações com serviços digitais de saúde."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(patients.router)
app.include_router(auth.router)
app.include_router(appointments.router)
app.include_router(exams.router)
app.include_router(vaccines.router)
app.include_router(medications.router)
app.include_router(health_units.router)
app.include_router(history.router)
app.include_router(referrals.router)


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }

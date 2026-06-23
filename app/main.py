from fastapi import FastAPI

from app.routers import (
    appointments,
    auth,
    chat,
    clinics,
    doctors,
    knowledge,
    patients,
    schedules,
    services,
)

app = FastAPI(title="Dental AI Call Center")

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(clinics.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(services.router)
app.include_router(appointments.router)
app.include_router(knowledge.router)
app.include_router(schedules.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
from fastapi import FastAPI
from app.routers import appointments, chat, clinics, doctors, patients, services
from app.routers import knowledge
from app.routers import schedules

app = FastAPI(title="Dental AI Call Center")

app.include_router(schedules.router)
app.include_router(knowledge.router)
app.include_router(chat.router)
app.include_router(clinics.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(services.router)
app.include_router(appointments.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
from fastapi import FastAPI
from app.routers import chat
from fastapi import FastAPI
from app.routers import chat, appointments

app = FastAPI(title="Dental AI Call Center")

app.include_router(chat.router)
app.include_router(appointments.router)


@app.get("/")
def health_check():
    return {"status": "ok"}


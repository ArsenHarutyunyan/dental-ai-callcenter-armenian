from fastapi import FastAPI
from app.routers import chat

app = FastAPI(title="Dental AI Call Center")

app.include_router(chat.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
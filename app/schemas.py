from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    patient_name: str
    phone: str
    complaint: str
    preferred_time: str | None = None
from pydantic import BaseModel


class ClinicCreate(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None


class ClinicUpdate(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None


class UserCreate(BaseModel):
    clinic_id: int | None = None
    full_name: str
    email: str
    password: str
    role: str = "operator"


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    clinic_id: int | None = None
    full_name: str
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class PatientCreate(BaseModel):
    full_name: str
    phone: str


class PatientUpdate(BaseModel):
    full_name: str
    phone: str


class DoctorCreate(BaseModel):
    clinic_id: int
    full_name: str
    specialization: str | None = None


class DoctorUpdate(BaseModel):
    clinic_id: int
    full_name: str
    specialization: str | None = None


class ServiceCreate(BaseModel):
    clinic_id: int
    name: str
    description: str | None = None
    price: int | None = None


class ServiceUpdate(BaseModel):
    clinic_id: int
    name: str
    description: str | None = None
    price: int | None = None


class AppointmentCreate(BaseModel):
    patient_name: str
    phone: str
    complaint: str
    preferred_time: str | None = None
    clinic_id: int | None = None
    patient_id: int | None = None
    doctor_id: int | None = None
    service_id: int | None = None
    schedule_id: int | None = None
    status: str = "new"


class AppointmentUpdate(BaseModel):
    patient_name: str
    phone: str
    complaint: str
    preferred_time: str | None = None
    status: str = "new"


class ChatMessageCreate(BaseModel):
    session_id: str
    clinic_id: int
    role: str
    message: str


class KnowledgeBaseCreate(BaseModel):
    clinic_id: int
    category: str
    title: str
    content: str


class DoctorScheduleCreate(BaseModel):
    doctor_id: int
    date: str
    start_time: str
    end_time: str


class DoctorScheduleUpdate(BaseModel):
    status: str
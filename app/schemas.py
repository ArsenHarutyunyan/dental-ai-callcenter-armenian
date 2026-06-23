from pydantic import BaseModel


class ClinicCreate(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None


class PatientCreate(BaseModel):
    full_name: str
    phone: str


class DoctorCreate(BaseModel):
    clinic_id: int
    full_name: str
    specialization: str | None = None


class ServiceCreate(BaseModel):
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
    status: str = "new"
    
class AppointmentUpdate(BaseModel):
    patient_name: str
    phone: str
    complaint: str
    preferred_time: str | None = None
    status: str = "new"
    
class ClinicUpdate(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None
    
class PatientUpdate(BaseModel):
    full_name: str
    phone: str
    
class DoctorUpdate(BaseModel):
    clinic_id: int
    full_name: str
    specialization: str | None = None
    
class ServiceUpdate(BaseModel):
    clinic_id: int
    name: str
    description: str | None = None
    price: int | None = None
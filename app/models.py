from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    doctors = relationship("Doctor", back_populates="clinic")
    services = relationship("Service", back_populates="clinic")
    appointments = relationship("Appointment", back_populates="clinic")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False, index=True)

    appointments = relationship("Appointment", back_populates="patient")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    full_name = Column(String, nullable=False)
    specialization = Column(String, nullable=True)

    clinic = relationship("Clinic", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=True)

    clinic = relationship("Clinic", back_populates="services")
    appointments = relationship("Appointment", back_populates="service")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)

    patient_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    complaint = Column(String, nullable=False)
    preferred_time = Column(String, nullable=True)
    status = Column(String, default="new")
    schedule_id = Column(Integer, ForeignKey("doctor_schedules.id"), nullable=True)
    clinic = relationship("Clinic", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(String, nullable=False, index=True)
    clinic_id = Column(Integer, nullable=False)

    role = Column(String, nullable=False)
    message = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    
class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)

    clinic_id = Column(Integer, nullable=False)

    category = Column(String, nullable=False)
    title = Column(String, nullable=False)

    content = Column(String, nullable=False)
    
class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id = Column(Integer, primary_key=True, index=True)

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False,
    )

    date = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    status = Column(String, default="available")

    doctor = relationship("Doctor")
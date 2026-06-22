from sqlalchemy import Column, Integer, String
from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    complaint = Column(String, nullable=False)
    preferred_time = Column(String, nullable=True)
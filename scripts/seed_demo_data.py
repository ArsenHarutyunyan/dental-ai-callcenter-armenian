"""Minimal demo data so the voice pipeline can be tested end-to-end."""
from app.database import SessionLocal
from app.models import Clinic, Doctor, Service, DoctorSchedule, KnowledgeBase

db = SessionLocal()

clinic = db.query(Clinic).filter(Clinic.name == "Demo Dental").first()
if not clinic:
    clinic = Clinic(name="Demo Dental", address="Երևան, Մաշտոցի պող. 1", phone="+37410000000")
    db.add(clinic)
    db.commit()
    db.refresh(clinic)

doctor = db.query(Doctor).filter(Doctor.clinic_id == clinic.id).first()
if not doctor:
    doctor = Doctor(clinic_id=clinic.id, full_name="Դր. Հակոբյան", specialization="Թերապևտ")
    db.add(doctor)
    db.commit()
    db.refresh(doctor)

if not db.query(Service).filter(Service.clinic_id == clinic.id).first():
    db.add(Service(clinic_id=clinic.id, name="Կոնսուլտացիա", description="Առաջնային զննում", price=5000))
    db.add(Service(clinic_id=clinic.id, name="Ատամի բուժում", description="Կարիես", price=25000))

if not db.query(DoctorSchedule).filter(DoctorSchedule.doctor_id == doctor.id).first():
    db.add(DoctorSchedule(doctor_id=doctor.id, date="2026-09-10", start_time="15:00", end_time="15:30", status="available"))
    db.add(DoctorSchedule(doctor_id=doctor.id, date="2026-09-10", start_time="16:00", end_time="16:30", status="available"))

if not db.query(KnowledgeBase).filter(KnowledgeBase.clinic_id == clinic.id).first():
    db.add(KnowledgeBase(
        clinic_id=clinic.id, category="working_hours", title="Աշխատանքային ժամեր",
        content="Կլինիկան աշխատում է երկուշաբթիից շաբաթ, ժամը 09:00-ից 19:00-ը։",
    ))
    db.add(KnowledgeBase(
        clinic_id=clinic.id, category="address", title="Հասցե",
        content="Երևան, Մաշտոցի պողոտա 1։",
    ))

db.commit()
print("clinic_id:", clinic.id, "doctor_id:", doctor.id)
print("seeded ok")

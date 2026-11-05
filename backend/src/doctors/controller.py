from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import re

from src.doctor_hospitals.models import DoctorHospital, AffiliationStatus
from src.hospitals.models import Hospital
from src.reviews.controller import get_doctor_rating_summary
from src.doctors.models import Doctor
from src.doctors.dtos import DoctorSignup, DoctorLogin, TokenResponse, DoctorProfileUpdate, ForgotPasswordRequest, ResetPasswordRequest
from src.specializations.models import Specialization
from src.utils.helpers import (
    hash_password,
    verify_password,
    create_access_token,
    create_email_token,
    decode_email_token,
    normalize_doctor_name,
)
from src.utils.settings import settings
from src.utils.mails import send_verification_email, send_password_reset_email
from src.utils.cloudinary import upload_file_to_cloudinary


def signup_doctor(signup_data: DoctorSignup, background_tasks: BackgroundTasks, db: Session) -> Doctor:
    existing = db.query(Doctor).filter(Doctor.email == signup_data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    specialization = db.query(Specialization).filter(
        Specialization.id == signup_data.specialization_id
    ).first()
    if not specialization:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid specialization selected.")

    doctor = Doctor(
        email=signup_data.email,
        hashed_password=hash_password(signup_data.password),
        name=normalize_doctor_name(signup_data.name),
        specialization_id=signup_data.specialization_id,
        qualifications=signup_data.qualifications,
        experience_years=signup_data.experience_years,
        bio=signup_data.bio,
        is_verified=not settings.EMAIL_VERIFICATION_ENABLED,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    if settings.EMAIL_VERIFICATION_ENABLED:
        verification_token = create_email_token({"doctor_id": doctor.id}, purpose="verify")
        background_tasks.add_task(send_verification_email, doctor.email, verification_token, "doctor")

    return doctor


def verify_doctor_email(token: str, db: Session) -> dict:
    payload = decode_email_token(token, expected_purpose="verify")
    doctor = db.query(Doctor).filter(Doctor.id == payload.get("doctor_id")).first()

    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

    if doctor.is_verified:
        return {"message": "Email already verified."}

    doctor.is_verified = True
    db.commit()

    return {"message": "Email verified successfully. You can now log in."}


def login_doctor(login_data: DoctorLogin, db: Session) -> TokenResponse:
    doctor = db.query(Doctor).filter(Doctor.email == login_data.email).first()

    if not doctor or not verify_password(login_data.password, doctor.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    if not doctor.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email before logging in.")

    access_token = create_access_token({"doctor_id": doctor.id, "role": "doctor"})
    return TokenResponse(access_token=access_token)

def update_doctor_profile(update_data: DoctorProfileUpdate, current_doctor: Doctor, db: Session) -> Doctor:
    update_fields = update_data.model_dump(exclude_unset=True)

    if "specialization_id" in update_fields:
        specialization = db.query(Specialization).filter(
            Specialization.id == update_fields["specialization_id"]
        ).first()
        if not specialization:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid specialization selected.")
        
    if "name" in update_fields:
        update_fields["name"] = normalize_doctor_name(update_fields["name"])

    for field, value in update_fields.items():
        setattr(current_doctor, field, value)

    db.commit()
    db.refresh(current_doctor)
    return current_doctor


def upload_doctor_profile_photo(file_bytes: bytes, filename: str, current_doctor: Doctor, db: Session) -> Doctor:
    image_url = upload_file_to_cloudinary(file_bytes, filename, folder="mediconnect/doctors/profile_photos")

    current_doctor.profile_image_url = image_url
    db.commit()
    db.refresh(current_doctor)

    return current_doctor


def forgot_doctor_password(request_data: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session) -> dict:
    doctor = db.query(Doctor).filter(Doctor.email == request_data.email).first()

    if doctor:
        reset_token = create_email_token({"doctor_id": doctor.id}, purpose="reset", expire_hours=1)
        background_tasks.add_task(send_password_reset_email, doctor.email, reset_token, "doctor")

    return {"message": "If an account with that email exists, a password reset link has been sent."}


def reset_doctor_password(request_data: ResetPasswordRequest, db: Session) -> dict:
    payload = decode_email_token(request_data.token, expected_purpose="reset")
    doctor = db.query(Doctor).filter(Doctor.id == payload.get("doctor_id")).first()

    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

    doctor.hashed_password = hash_password(request_data.new_password)
    db.commit()

    return {"message": "Password reset successfully. You can now log in with your new password."}


def search_doctors(db: Session, city_id: int = None, specialization_id: int = None, doctor_name: str = None, hospital_name: str = None, skip: int = 0, limit: int = 20) -> dict:
    query = db.query(DoctorHospital).join(Hospital).join(Doctor).filter(
        DoctorHospital.status == AffiliationStatus.approved,
        DoctorHospital.is_available == True,
    )

    if city_id:
        query = query.filter(Hospital.city_id == city_id)
    if specialization_id:
        query = query.filter(Doctor.specialization_id == specialization_id)
    if doctor_name:
        # Patients/LLM callers inconsistently include "Dr"/"Dr." — strip it
        # so matching doesn't depend on whether the title was included.
        cleaned_name = re.sub(r"(?i)^\s*dr\.?\s+", "", doctor_name.strip())
        query = query.filter(Doctor.name.ilike(f"%{cleaned_name}%"))
    if hospital_name:
        # Callers (including the AI agent) often say "X Hospital" even when
        # the stored name is just "X" -- strip a trailing generic word so
        # the search isn't defeated by a suffix the data doesn't have.
        # This only ever widens the match, never narrows it.
        cleaned_hospital = re.sub(
            r"(?i)\s*(hospital|clinic|medical center|medical centre)\s*$",
            "",
            hospital_name.strip(),
        ).strip() or hospital_name.strip()
        query = query.filter(Hospital.name.ilike(f"%{cleaned_hospital}%"))

    total = query.count()
    affiliations = query.offset(skip).limit(limit).all()

    results = []
    for affiliation in affiliations:
        doctor = affiliation.doctor
        hospital = affiliation.hospital
        rating_summary = get_doctor_rating_summary(doctor.id, db)
        results.append({
            "doctor_hospital_id": affiliation.id,
            "doctor_id": doctor.id,
            "doctor_name": doctor.name,
            "specialization_id": doctor.specialization_id,
            "specialization_name": doctor.specialization.name,
            "qualifications": doctor.qualifications,
            "experience_years": doctor.experience_years,
            "bio": doctor.bio,
            "profile_image_url": doctor.profile_image_url,
            "fee": affiliation.fee,
            "days": affiliation.days,
            "start_time": affiliation.start_time,
            "end_time": affiliation.end_time,
            "patients_per_day": affiliation.patients_per_day,
            "avg_rating": rating_summary["avg_rating"],
            "review_count": rating_summary["review_count"],
            "hospital_id": hospital.id,
            "hospital_name": hospital.name,
            "hospital_address": hospital.address,
            "city_id": hospital.city_id,
            "city_name": hospital.city.name,
        })

    return {"total": total, "skip": skip, "limit": limit, "items": results}
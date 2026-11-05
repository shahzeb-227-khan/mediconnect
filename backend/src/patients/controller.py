from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from src.patients.models import Patient
from src.patients.dtos import (
    PatientSignup,
    PatientLogin,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    PatientProfileUpdate,
    ChangeEmailRequest,
    ChangePasswordRequest,
)
from src.utils.helpers import (
    hash_password,
    verify_password,
    create_access_token,
    create_email_token,
    decode_email_token,
)
from src.utils.settings import settings
from src.utils.mails import send_verification_email, send_password_reset_email, send_email_change_verification


def signup_patient(signup_data: PatientSignup, background_tasks: BackgroundTasks, db: Session) -> Patient:
    existing = db.query(Patient).filter(Patient.email == signup_data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    patient = Patient(
        email=signup_data.email,
        hashed_password=hash_password(signup_data.password),
        name=signup_data.name,
        phone_number=signup_data.phone_number,
        is_verified=not settings.EMAIL_VERIFICATION_ENABLED,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    if settings.EMAIL_VERIFICATION_ENABLED:
        verification_token = create_email_token({"patient_id": patient.id}, purpose="verify")
        background_tasks.add_task(send_verification_email, patient.email, verification_token, "patient")

    return patient


def verify_patient_email(token: str, db: Session) -> dict:
    payload = decode_email_token(token, expected_purpose="verify")
    patient = db.query(Patient).filter(Patient.id == payload.get("patient_id")).first()

    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")

    if patient.is_verified:
        return {"message": "Email already verified."}

    patient.is_verified = True
    db.commit()

    return {"message": "Email verified successfully. You can now log in."}


def login_patient(login_data: PatientLogin, db: Session) -> TokenResponse:
    patient = db.query(Patient).filter(Patient.email == login_data.email).first()

    if not patient or not verify_password(login_data.password, patient.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    if not patient.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email before logging in.")

    access_token = create_access_token({"patient_id": patient.id, "role": "patient"})
    return TokenResponse(access_token=access_token)


def forgot_patient_password(request_data: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session) -> dict:
    patient = db.query(Patient).filter(Patient.email == request_data.email).first()

    if patient:
        reset_token = create_email_token({"patient_id": patient.id}, purpose="reset", expire_hours=1)
        background_tasks.add_task(send_password_reset_email, patient.email, reset_token, "patient")

    return {"message": "If an account with that email exists, a password reset link has been sent."}


def reset_patient_password(request_data: ResetPasswordRequest, db: Session) -> dict:
    payload = decode_email_token(request_data.token, expected_purpose="reset")
    patient = db.query(Patient).filter(Patient.id == payload.get("patient_id")).first()

    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")

    patient.hashed_password = hash_password(request_data.new_password)
    db.commit()

    return {"message": "Password reset successfully. You can now log in with your new password."}


def update_patient_profile(update_data: PatientProfileUpdate, current_patient: Patient, db: Session) -> Patient:
    update_fields = update_data.model_dump(exclude_unset=True)

    for field, value in update_fields.items():
        setattr(current_patient, field, value)

    db.commit()
    db.refresh(current_patient)
    return current_patient


def request_email_change(request_data: ChangeEmailRequest, background_tasks: BackgroundTasks, current_patient: Patient, db: Session) -> dict:
    existing = db.query(Patient).filter(Patient.email == request_data.new_email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This email is already in use.")

    # The new email lives inside the token itself (not in a DB column) --
    # nothing changes on the account until the link is actually clicked.
    token = create_email_token(
        {"patient_id": current_patient.id, "new_email": request_data.new_email},
        purpose="change_email",
    )
    background_tasks.add_task(send_email_change_verification, request_data.new_email, token)

    return {"message": "A verification link has been sent to your new email address."}


def confirm_email_change(token: str, db: Session) -> dict:
    payload = decode_email_token(token, expected_purpose="change_email")
    patient = db.query(Patient).filter(Patient.id == payload.get("patient_id")).first()

    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")

    new_email = payload.get("new_email")

    # Re-check for a collision at confirmation time too -- someone else could
    # have registered this exact email in the time between the request and
    # the click.
    existing = db.query(Patient).filter(Patient.email == new_email, Patient.id != patient.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This email is already in use.")

    patient.email = new_email
    db.commit()

    return {"message": "Email address updated successfully. Please log in again."}


def change_patient_password(request_data: ChangePasswordRequest, current_patient: Patient, db: Session) -> dict:
    if not verify_password(request_data.current_password, current_patient.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect.")

    current_patient.hashed_password = hash_password(request_data.new_password)
    db.commit()

    return {"message": "Password changed successfully."}
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from src.utils.settings import settings

from src.utils.database import engine
from src.utils.limiter import limiter

from src.cities.models import City
from src.specializations.models import Specialization
from src.hospitals.models import Hospital
from src.doctors.models import Doctor
from src.doctor_hospitals.models import DoctorHospital
from src.patients.models import Patient
from src.appointments.models import Appointment
from src.reviews.models import Review

from src.patients.router import patients_router
from src.doctors.router import doctors_router
from src.admin.router import admin_router
from src.doctor_hospitals.router import doctor_hospitals_router
from src.hospitals.router import hospitals_router
from src.appointments.router import appointments_router
from src.reviews.router import reviews_router
from src.cities.router import cities_router
from src.specializations.router import specializations_router
from src.ai.router import ai_router
from src.assistant.router import assistant_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("mediconnect")

app = FastAPI(title="MediConnect")


@app.on_event("startup")
def auto_verify_existing_users():
    """When email verification is disabled (demo env), unblock accounts created earlier."""
    if settings.EMAIL_VERIFICATION_ENABLED:
        return
    try:
        with engine.begin() as connection:
            connection.execute(text("UPDATE patients SET is_verified = TRUE WHERE is_verified = FALSE"))
            connection.execute(text("UPDATE doctors SET is_verified = TRUE WHERE is_verified = FALSE"))
        logger.info("Email verification disabled: existing accounts marked verified")
    except SQLAlchemyError:
        logger.exception("Could not auto-verify existing accounts")

cors_origins = [settings.ORIGIN_URL]
if settings.CORS_ORIGINS:
    cors_origins.extend(
        origin.strip()
        for origin in settings.CORS_ORIGINS.split(",")
        if origin.strip()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception while processing %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients_router)
app.include_router(doctors_router)
app.include_router(admin_router)
app.include_router(doctor_hospitals_router)
app.include_router(hospitals_router)
app.include_router(appointments_router)
app.include_router(reviews_router)
app.include_router(cities_router)
app.include_router(specializations_router)
app.include_router(ai_router)
app.include_router(assistant_router)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
async def read_root():
    return {"status": "MediConnect API is running"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/health/db")
async def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Database health check failed")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": "Database is unavailable"},
        )

    return {"status": "ok"}
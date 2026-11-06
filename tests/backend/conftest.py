"""Shared fixtures for the MediConnect backend tests.

The tests run against a real PostgreSQL database (the same engine as production).
In CI it is a service container; locally use the docker-compose database, e.g.

    set TEST_DATABASE_URL=postgresql+psycopg2://internship_user:internship_pass@localhost:5432/mediconnect_test

Safety: the database name must contain "test", because the fixtures create and
drop every table.
"""
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/mediconnect_test",
)
if "test" not in TEST_DATABASE_URL.rsplit("/", 1)[-1].lower():
    raise RuntimeError("Refusing to run: the test database name must contain 'test'.")

# Test-only configuration. Assigned (not setdefault) so real secrets are never used.
os.environ.update(
    {
        "DATABASE_URL": TEST_DATABASE_URL,
        "JWT_SECRET_KEY": "test-secret-key-used-only-in-automated-tests",
        "JWT_ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "ADMIN_EMAIL": "admin@test.local",
        "ADMIN_PASSWORD": "AdminPass123",
        "MAIL_USERNAME": "test",
        "MAIL_PASSWORD": "test",
        "MAIL_FROM": "noreply@test.local",
        "MAIL_PORT": "587",
        "MAIL_SERVER": "localhost",
        "MAIL_FROM_NAME": "MediConnect Tests",
        "ORIGIN_URL": "http://localhost",
        "CLOUDINARY_CLOUD_NAME": "test",
        "CLOUDINARY_API_KEY": "test",
        "CLOUDINARY_API_SECRET": "test",
        "STRIPE_SECRET_KEY": "sk_test_dummy",
        "STRIPE_PUBLISHABLE_KEY": "pk_test_dummy",
        "STRIPE_WEBHOOK_SECRET": "whsec_dummy",
        "GEMINI_API_KEY": "test-key",
        "EMAIL_VERIFICATION_ENABLED": "false",
    }
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402  (imports every model and router)
from src.utils.database import Base, engine  # noqa: E402
from src.utils.limiter import limiter  # noqa: E402
from src.utils.settings import settings  # noqa: E402

limiter.enabled = False  # login and signup are rate limited in production


@pytest.fixture(scope="session", autouse=True)
def database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def clean_tables(database):
    """Empty every table after each test so tests do not affect each other."""
    yield
    names = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
    with engine.begin() as connection:
        connection.exec_driver_sql(f"TRUNCATE {names} RESTART IDENTITY CASCADE")


@pytest.fixture()
def client():
    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture()
def no_email(monkeypatch):
    """Replace the SMTP senders so no test tries to send a real email."""
    async def _skip(*args, **kwargs):
        return None

    monkeypatch.setattr("src.patients.controller.send_verification_email", _skip)
    monkeypatch.setattr("src.patients.controller.send_password_reset_email", _skip)
    monkeypatch.setattr("src.patients.controller.send_email_change_verification", _skip)


@pytest.fixture()
def admin_headers(client):
    response = client.post(
        "/admin/login",
        json={"email": settings.ADMIN_EMAIL, "password": settings.ADMIN_PASSWORD},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture()
def patient_headers(client, no_email):
    payload = {"email": "ali@test.local", "password": "Strong123", "name": "Ali"}
    assert client.post("/patients/signup", json=payload).status_code == 200
    login = client.post("/patients/login", json={"email": payload["email"], "password": payload["password"]})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}

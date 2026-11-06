"""Input validation rules (Pydantic models)."""
import pytest
from pydantic import ValidationError

from src.patients.dtos import PatientSignup


def make(password="Strong123", email="a@mediconnect-demo.com"):
    return PatientSignup(email=email, password=password, name="Ali")


def test_valid_signup_is_accepted():
    assert make().email == "a@mediconnect-demo.com"


@pytest.mark.parametrize("password", ["Short1", "nouppercase1", "NoNumberHere"])
def test_weak_passwords_are_rejected(password):
    with pytest.raises(ValidationError):
        make(password=password)


def test_invalid_email_is_rejected():
    with pytest.raises(ValidationError):
        make(email="not-an-email")

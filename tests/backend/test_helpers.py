"""Unit tests for authentication and utility helpers (no HTTP, no database rows)."""
from datetime import datetime, time, timedelta

import jwt
import pytest
from fastapi import HTTPException

from src.utils import helpers
from src.utils.settings import settings


def test_password_is_hashed_and_verifies():
    hashed = helpers.hash_password("Strong123")
    assert hashed != "Strong123"
    assert helpers.verify_password("Strong123", hashed)


def test_wrong_password_is_rejected():
    hashed = helpers.hash_password("Strong123")
    assert not helpers.verify_password("Wrong123", hashed)


def test_same_password_gets_different_hashes():
    assert helpers.hash_password("Strong123") != helpers.hash_password("Strong123")


def test_access_token_round_trip():
    token = helpers.create_access_token({"patient_id": 7, "role": "patient"})
    payload = helpers.decode_access_token(token)
    assert payload["patient_id"] == 7
    assert payload["role"] == "patient"
    assert "exp" in payload


def test_garbage_token_is_rejected():
    with pytest.raises(HTTPException) as error:
        helpers.decode_access_token("not-a-token")
    assert error.value.status_code == 401


def test_expired_token_is_rejected():
    expired = jwt.encode(
        {"role": "patient", "exp": datetime.now() - timedelta(minutes=5)},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(HTTPException) as error:
        helpers.decode_access_token(expired)
    assert error.value.status_code == 401


def test_token_signed_with_another_key_is_rejected():
    forged = jwt.encode({"role": "admin"}, "some-other-secret-key-0123456789", algorithm="HS256")
    with pytest.raises(HTTPException) as error:
        helpers.decode_access_token(forged)
    assert error.value.status_code == 401


def test_email_token_accepts_matching_purpose():
    token = helpers.create_email_token({"patient_id": 1}, purpose="verify")
    assert helpers.decode_email_token(token, "verify")["patient_id"] == 1


def test_email_token_rejects_other_purpose():
    token = helpers.create_email_token({"patient_id": 1}, purpose="verify")
    with pytest.raises(HTTPException) as error:
        helpers.decode_email_token(token, "reset")
    assert error.value.status_code == 400


@pytest.mark.parametrize(
    "text, expected",
    [("9:00", time(9, 0)), ("21:30", time(21, 30)), ("07:05", time(7, 5)), (" 8:15 ", time(8, 15))],
)
def test_time_strings_are_normalised(text, expected):
    assert helpers.normalize_time_string(text) == expected


@pytest.mark.parametrize("text", ["abc", "25:00", "12:99"])
def test_invalid_time_strings_are_rejected(text):
    with pytest.raises(HTTPException) as error:
        helpers.normalize_time_string(text)
    assert error.value.status_code == 400


@pytest.mark.parametrize(
    "name, expected",
    [("Dr. Ali", "Ali"), ("dr Ali Khan", "Ali Khan"), ("Doctor Sara", "Sara"), ("Ali", "Ali")],
)
def test_doctor_name_prefix_is_removed(name, expected):
    assert helpers.normalize_doctor_name(name) == expected

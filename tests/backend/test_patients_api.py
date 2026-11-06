"""Patient registration, login and protected routes, against the real database."""
SIGNUP = {"email": "ali@mediconnect-demo.com", "password": "Strong123", "name": "Ali", "phone_number": "0300"}


def test_signup_creates_verified_account_when_verification_is_off(client, no_email):
    response = client.post("/patients/signup", json=SIGNUP)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == SIGNUP["email"]
    assert body["is_verified"] is True
    assert "password" not in body and "hashed_password" not in body


def test_duplicate_email_is_rejected(client, no_email):
    assert client.post("/patients/signup", json=SIGNUP).status_code == 200
    second = client.post("/patients/signup", json=SIGNUP)
    assert second.status_code == 400
    assert second.json()["detail"] == "Email already registered."


def test_weak_password_is_rejected_with_422(client, no_email):
    response = client.post("/patients/signup", json={**SIGNUP, "password": "weak"})
    assert response.status_code == 422


def test_login_returns_token_and_profile_works(client, no_email):
    client.post("/patients/signup", json=SIGNUP)
    login = client.post("/patients/login", json={"email": SIGNUP["email"], "password": SIGNUP["password"]})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    token = login.json()["access_token"]
    me = client.get("/patients/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == SIGNUP["email"]


def test_wrong_password_is_unauthorized(client, no_email):
    client.post("/patients/signup", json=SIGNUP)
    response = client.post("/patients/login", json={"email": SIGNUP["email"], "password": "Wrong123"})
    assert response.status_code == 401


def test_unknown_email_is_unauthorized(client):
    response = client.post("/patients/login", json={"email": "nobody@mediconnect-demo.com", "password": "Strong123"})
    assert response.status_code == 401


def test_unverified_account_cannot_log_in_when_verification_is_on(client, no_email, monkeypatch):
    from src.utils.settings import settings

    monkeypatch.setattr(settings, "EMAIL_VERIFICATION_ENABLED", True)
    signup = client.post("/patients/signup", json=SIGNUP)
    assert signup.status_code == 200
    assert signup.json()["is_verified"] is False
    login = client.post("/patients/login", json={"email": SIGNUP["email"], "password": SIGNUP["password"]})
    assert login.status_code == 403


def test_profile_can_be_updated(client, patient_headers):
    response = client.patch("/patients/me", json={"name": "Ali Khan"}, headers=patient_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Ali Khan"


def test_profile_without_token_is_rejected(client):
    assert client.get("/patients/me").status_code in (401, 403)


def test_profile_with_invalid_token_is_unauthorized(client):
    response = client.get("/patients/me", headers={"Authorization": "Bearer garbage"})
    assert response.status_code == 401


def test_forgot_password_does_not_reveal_whether_email_exists(client, no_email):
    response = client.post("/patients/forgot-password", json={"email": "nobody@mediconnect-demo.com"})
    assert response.status_code == 200
    assert "reset link" in response.json()["message"]

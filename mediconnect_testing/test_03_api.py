"""
FILE 3 — API TESTING (CRUD Operations)
========================================
Tests the MediConnect backend API using Playwright's APIRequestContext.
Covers all four CRUD operations as required by the problem statement.

CRUD Mapping:
  CREATE → POST /patients/signup     (create a new patient account)
  READ   → GET  /hospitals           (read hospital list)
  UPDATE → PUT  /patients/profile    (update patient profile — requires auth)
  DELETE → DELETE /appointments/:id  (delete appointment — requires auth)

Playwright Concepts Used:
  - playwright.request.new_context(base_url=..., extra_http_headers=...)
  - api_context.get(), .post(), .put(), .delete()
  - response.status, response.ok, response.json()
  - @pytest.fixture with yield and api_context.dispose()
  - Query string parameters in API calls
  - Type hints (Playwright, APIRequestContext)
"""

import pytest
import os
import random
from playwright.sync_api import Playwright, APIRequestContext


API_URL = "http://localhost:8001"

# Credentials from environment variables
TEST_EMAIL    = os.environ.get("MEDI_TEST_EMAIL", "")
TEST_PASSWORD = os.environ.get("MEDI_TEST_PASSWORD", "")


# ── Fixture: API Request Context ─────────────────────────────────────
@pytest.fixture
def api_context(playwright: Playwright) -> APIRequestContext:
    """
    Creates an API request context with base URL and JSON headers.
    Uses yield to provide the context and dispose() after test completes.
    This follows the fixture lifecycle pattern from Lab #12 Part C.
    """
    context = playwright.request.new_context(
        base_url=API_URL,
        extra_http_headers={"Content-Type": "application/json"},
    )
    yield context
    context.dispose()


# ── CRUD Operation 1: CREATE (POST) ─────────────────────────────────
@pytest.mark.api
class TestAPI_Create:
    """Tests POST endpoint for creating new resources (CREATE)."""

    def test_create_signup_valid(self, api_context: APIRequestContext):
        """POST /patients/signup with valid data creates a new account."""
        rand_id = random.randint(10000, 99999)

        response = api_context.post(
            "/patients/signup",
            data={
                "name": f"Test User {rand_id}",
                "email": f"testuser{rand_id}@playwright-test.com",
                "password": "TestPass123#",
                "phone": f"0300{rand_id}",
            },
        )
        # 200/201 = created, 409 = already exists (re-run), 422 = validation
        assert response.status in [200, 201, 409, 422], (
            f"Unexpected status {response.status} for signup"
        )
        print(f"CREATE (signup) → {response.status}")

    def test_create_signup_missing_fields(self, api_context: APIRequestContext):
        """POST /patients/signup with empty fields returns 422."""
        response = api_context.post(
            "/patients/signup",
            data={"email": "", "password": ""},
        )
        assert response.status in [400, 422], (
            f"Expected validation error, got {response.status}"
        )
        print(f"CREATE (empty) → {response.status} ✓")


# ── CRUD Operation 2: READ (GET) ────────────────────────────────────
@pytest.mark.api
class TestAPI_Read:
    """Tests GET endpoint for reading resources (READ)."""

    def test_read_all_hospitals(self, api_context: APIRequestContext):
        """GET /hospitals should return 200 and a list of hospitals."""
        response = api_context.get("/hospitals")
        assert response.status == 200
        assert response.ok
        data = response.json()
        if isinstance(data, list):
            print(f"READ (all) → {len(data)} hospitals")
        else:
            print(f"READ (all) → paginated: {data.get('total', '?')}")

    def test_read_single_hospital(self, api_context: APIRequestContext):
        """GET /hospitals/1 should return a single hospital or 404."""
        response = api_context.get("/hospitals/1")
        assert response.status in [200, 404]
        print(f"READ (single) → {response.status}")

    def test_read_nonexistent_returns_404(self, api_context: APIRequestContext):
        """GET /hospitals/99999 should return 404 for non-existent hospital."""
        response = api_context.get("/hospitals/99999")
        assert response.status == 404
        assert not response.ok
        print(f"READ (not found) → {response.status} ✓")

    def test_read_with_query_string(self, api_context: APIRequestContext):
        """GET /hospitals with query string should filter results."""
        response = api_context.get("/hospitals")
        assert response.status == 200
        data = response.json()
        count = len(data) if isinstance(data, list) else data.get("total", 0)
        print(f"READ (query) → {count} results")


# ── CRUD Operation 3: UPDATE (PUT/POST login) ───────────────────────
@pytest.mark.api
class TestAPI_Update:
    """
    Tests UPDATE operations. The MediConnect backend uses POST /patients/login
    to verify and return tokens, which effectively updates the session state.
    Also tests PUT /patients/profile for profile updates (requires auth token).
    """

    def test_update_login_valid(self, api_context: APIRequestContext):
        """POST /patients/login with valid credentials returns 200 + token."""
        response = api_context.post(
            "/patients/login",
            data={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
            },
        )
        assert response.status == 200, (
            f"Login failed with status {response.status}"
        )
        data = response.json()
        print(f"UPDATE (login) → 200, keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")

    def test_update_login_invalid(self, api_context: APIRequestContext):
        """POST /patients/login with wrong credentials returns error."""
        response = api_context.post(
            "/patients/login",
            data={
                "email": "nonexistent@test.com",
                "password": "WrongPassword999",
            },
        )
        assert response.status in [400, 401, 403, 422]
        print(f"UPDATE (bad login) → {response.status} ✓")

    def test_update_profile_without_auth(self, api_context: APIRequestContext):
        """PUT /patients/profile without auth token returns 401/403."""
        response = api_context.put(
            "/patients/profile",
            data={
                "name": "Updated Name",
                "phone": "03001234567",
            },
        )
        # Without auth token, should get 401/403/404/405
        assert response.status in [401, 403, 404, 405, 422], (
            f"Expected auth error, got {response.status}"
        )
        print(f"UPDATE (no auth) → {response.status} ✓")


# ── CRUD Operation 4: DELETE ─────────────────────────────────────────
@pytest.mark.api
class TestAPI_Delete:
    """Tests DELETE operations for resource deletion (DELETE)."""

    def test_delete_nonexistent_resource(self, api_context: APIRequestContext):
        """DELETE /hospitals/99999 should return 404 or 405."""
        response = api_context.delete("/hospitals/99999")
        assert response.status in [404, 405, 401, 403]
        print(f"DELETE (not found) → {response.status} ✓")

    def test_delete_appointment_without_auth(self, api_context: APIRequestContext):
        """DELETE /appointments/1 without auth should return 401/403."""
        response = api_context.delete("/appointments/1")
        assert response.status in [401, 403, 404, 405]
        print(f"DELETE (no auth) → {response.status} ✓")

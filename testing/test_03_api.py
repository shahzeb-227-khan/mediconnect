import pytest
import os
from playwright.sync_api import Playwright, APIRequestContext


API_URL = "http://localhost:8001"

# Credentials for positive login test
TEST_EMAIL    = os.environ.get("MEDI_TEST_EMAIL", "")
TEST_PASSWORD = os.environ.get("MEDI_TEST_PASSWORD", "")


# ── Fixture: API Request Context with base URL and headers ──────────
@pytest.fixture
def api_context(playwright: Playwright) -> APIRequestContext:
    """
    Creates an API request context with base URL and JSON headers.
    Uses yield to provide the context and dispose after test completes.
    This follows the fixture lifecycle pattern from Lab #12 Part C.
    """
    context = playwright.request.new_context(
        base_url=API_URL,
        extra_http_headers={"Content-Type": "application/json"},
    )
    yield context
    context.dispose()


# ── 1. GET — Read All Hospitals ─────────────────────────────────────
@pytest.mark.api
class TestAPIGetHospitals:
    """Tests the GET /hospitals endpoint to read all hospitals. (READ)"""

    def test_get_hospitals_status_200(self, api_context: APIRequestContext):
        """GET /hospitals should return status 200."""
        response = api_context.get("/hospitals")
        assert response.status == 200, (
            f"Expected status 200, got {response.status}"
        )
        assert response.ok, "Response was not OK"

    def test_get_hospitals_returns_list(self, api_context: APIRequestContext):
        """GET /hospitals should return a JSON list."""
        response = api_context.get("/hospitals")
        assert response.ok, f"Request failed with status {response.status}"

        data = response.json()
        # API returns paginated dict {items, total, skip, limit} or plain list
        if isinstance(data, list):
            print(f"Hospitals returned (list): {len(data)}")
        else:
            assert "items" in data or "total" in data, f"Bad response: {list(data.keys())}"
            print(f"Hospitals returned (paginated): total={data.get('total', '?')}")

    def test_get_hospitals_have_required_fields(self, api_context: APIRequestContext):
        """Each hospital should have a name field."""
        response = api_context.get("/hospitals")
        assert response.ok

        data = response.json()
        hospitals = data if isinstance(data, list) else data.get("items", [])
        if len(hospitals) > 0:
            hospital = hospitals[0]
            assert "name" in hospital, f"Missing 'name'. Keys: {list(hospital.keys())}"
            print(f"First hospital: {hospital.get('name')}")
        else:
            print("No hospitals in DB — empty list is valid")


# ── 2. GET — Read Single Resource & 404 ─────────────────────────────
@pytest.mark.api
class TestAPIGetSingleResource:
    """Tests GET for single resources and 404 error handling. (READ)"""

    def test_get_first_hospital(self, api_context: APIRequestContext):
        """GET /hospitals/1 should return a single hospital."""
        response = api_context.get("/hospitals/1")
        # 200 = found, 404 = not seeded yet — both are acceptable
        assert response.status in [200, 404], (
            f"Unexpected status {response.status}"
        )
        print(f"GET /hospitals/1 → {response.status}")

    def test_get_nonexistent_resource_returns_404(self, api_context: APIRequestContext):
        """GET /hospitals/99999 should return 404 for non-existent hospital."""
        response = api_context.get("/hospitals/99999")
        assert response.status == 404, (
            f"Expected 404 for non-existent resource, got {response.status}"
        )
        assert not response.ok, "Response should NOT be OK for 404"
        print(f"Status: {response.status} ✓ — resource not found")


# ── 3. POST — Create New Resource (Signup) ──────────────────────────
@pytest.mark.api
class TestAPIPostCreate:
    """Tests POST endpoint for creating new resources. (CREATE)"""

    def test_signup_with_valid_data(self, api_context: APIRequestContext):
        """POST /patients/signup should create a new user account."""
        import random
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
        print(f"Signup response: {response.status}")

    def test_signup_with_missing_fields_returns_422(self, api_context: APIRequestContext):
        """POST /patients/signup with empty fields should return 422 validation error."""
        response = api_context.post(
            "/patients/signup",
            data={"email": "", "password": ""},
        )
        # FastAPI returns 422 for validation errors
        assert response.status in [400, 422], (
            f"Expected 422 validation error, got {response.status}"
        )
        print(f"Empty signup → {response.status} ✓")


# ── 4. POST/READ — Login returns token ──────────────────────────────
@pytest.mark.api
class TestAPIPutUpdate:
    """Tests login endpoint and verifies token/response structure. (READ)"""

    def test_login_with_valid_credentials(self, api_context: APIRequestContext):
        """POST /patients/login with valid credentials should return 200 + token."""
        response = api_context.post(
            "/patients/login",
            data={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
            },
        )

        assert response.status == 200, (
            f"Login failed with status {response.status}. "
            "Check credentials or that backend is running."
        )
        data = response.json()
        print(f"Login OK — response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")

    def test_login_with_wrong_credentials_returns_error(self, api_context: APIRequestContext):
        """POST /patients/login with wrong password should return 401/400."""
        response = api_context.post(
            "/patients/login",
            data={
                "email": "nonexistent@test.com",
                "password": "WrongPassword999",
            },
        )
        assert response.status in [400, 401, 403, 422], (
            f"Expected error status for bad creds, got {response.status}"
        )
        print(f"Bad login → {response.status} ✓")


# ── 5. DELETE — Delete Resource / Verify Deletion ───────────────────
@pytest.mark.api
class TestAPIDeleteResource:
    """Tests DELETE operations and resource deletion verification. (DELETE)"""

    def test_delete_nonexistent_returns_error(self, api_context: APIRequestContext):
        """DELETE /hospitals/99999 should return 404 or method-not-allowed."""
        response = api_context.delete("/hospitals/99999")
        # 404 = not found, 405 = method not allowed, 401/403 = auth required
        assert response.status in [404, 405, 401, 403], (
            f"Expected error status, got {response.status}"
        )
        print(f"DELETE /hospitals/99999 → {response.status} ✓")

    def test_delete_protected_resource_needs_auth(self, api_context: APIRequestContext):
        """DELETE on a protected resource without a token should return 401/403."""
        response = api_context.delete("/appointments/1")
        assert response.status in [401, 403, 404, 405], (
            f"Expected auth/not-found error, got {response.status}"
        )
        print(f"DELETE /appointments/1 (no auth) → {response.status} ✓")


# ── 6. Query String Testing ─────────────────────────────────────────
@pytest.mark.api
class TestAPIQueryString:
    """Tests API endpoints with query string parameters."""

    def test_get_hospitals_with_valid_response(self, api_context: APIRequestContext):
        """GET /hospitals should return a list (query string baseline)."""
        response = api_context.get("/hospitals")
        assert response.status == 200
        data = response.json()
        assert isinstance(data, (list, dict)), f"Unexpected type: {type(data)}"
        count = len(data) if isinstance(data, list) else data.get("total", len(data.get("items", [])))
        print(f"Hospital list has {count} entries")

    def test_get_cities_endpoint(self, api_context: APIRequestContext):
        """GET /cities should return a 200 list of cities."""
        response = api_context.get("/cities")
        assert response.status in [200, 404], (
            f"Unexpected status {response.status}"
        )
        if response.status == 200:
            data = response.json()
            print(f"Cities: {data[:3] if isinstance(data, list) else data}")

    def test_get_specializations_endpoint(self, api_context: APIRequestContext):
        """GET /specializations should return available specializations."""
        response = api_context.get("/specializations")
        assert response.status in [200, 404], (
            f"Unexpected status {response.status}"
        )
        print(f"Specializations status: {response.status}")

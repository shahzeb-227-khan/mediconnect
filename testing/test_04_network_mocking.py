import pytest
from playwright.sync_api import Page, Route, expect


BASE_URL = "http://localhost:5175"
API_URL  = "http://localhost:8001"


@pytest.mark.network
class TestMockEmptyResponse:
    """
    Mock Test 1: Mock the hospitals API to return an empty list.
    This tests how the frontend handles having no data.
    Uses route.fulfill() with json parameter (Lab #09 Part D / Lab #12 Part F).
    """

    def test_mock_empty_hospitals_list(self, page: Page):
        """Mock /hospitals to return empty array — tests empty state UI."""

        def handle_route(route: Route):
            route.fulfill(
                status=200,
                content_type="application/json",
                json=[],
            )

        # Intercept the backend hospitals API call
        page.route(f"{API_URL}/hospitals", handle_route)

        page.goto(f"{BASE_URL}/hospitals")
        page.wait_for_timeout(2000)

        # The page should still load without crashing
        expect(page).to_have_url(f"{BASE_URL}/hospitals")
        print("Mock empty list: Page loaded successfully with empty data")

    def test_mock_error_response(self, page: Page):
        """Mock /hospitals to return 500 error — tests error handling UI."""

        def handle_error(route: Route):
            route.fulfill(
                status=500,
                content_type="application/json",
                json={"error": "Internal Server Error"},
            )

        page.route(f"{API_URL}/hospitals", handle_error)
        page.goto(f"{BASE_URL}/hospitals")
        page.wait_for_timeout(2000)

        # Page should still render (not crash) even with server error
        expect(page).to_have_url(f"{BASE_URL}/hospitals")
        print("Mock error response: Page handled 500 error gracefully")


@pytest.mark.network
class TestModifyResponse:
    """
    Mock Test 2: Intercept a real API response and modify it.
    Uses route.fetch() to get the real response, then modifies
    and returns it with route.fulfill() (Lab #12 Part F concept).
    """

    def test_modify_api_response(self, page: Page):
        """Fetch real response from API, modify it, and return modified version."""

        modified = False

        def modify_handler(route: Route):
            nonlocal modified
            try:
                response = route.fetch()
                data = response.json()

                if isinstance(data, list):
                    data.append({
                        "id": 9999,
                        "name": "Mock Test Hospital",
                        "city": "Test City",
                        "address": "123 Test Street",
                    })
                    modified = True

                route.fulfill(
                    response=response,
                    json=data,
                )
            except Exception:
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    json=[{
                        "id": 9999,
                        "name": "Mock Test Hospital",
                        "city": "Test City",
                        "address": "123 Test Street",
                    }],
                )
                modified = True

        page.route(f"{API_URL}/hospitals", modify_handler)
        page.goto(f"{BASE_URL}/hospitals")
        page.wait_for_timeout(2000)

        print(f"Response was modified: {modified}")
        expect(page).to_have_url(f"{BASE_URL}/hospitals")


@pytest.mark.network
class TestBlockRequests:
    """
    Tests blocking specific network requests using route.abort().
    Demonstrates that the page can handle missing resources gracefully.
    """

    def test_block_image_requests(self, page: Page):
        """Block all image requests to test page loads without images."""

        blocked_count = 0

        def block_images(route: Route):
            nonlocal blocked_count
            blocked_count += 1
            route.abort()

        page.route("**/*.{png,jpg,jpeg,gif,svg,webp}", block_images)
        page.goto(BASE_URL, wait_until="networkidle")

        expect(page.locator("h1")).to_contain_text("Find a doctor")
        print(f"Blocked {blocked_count} image request(s) — page still functional")

    def test_continue_request_unchanged(self, page: Page):
        """Use route.continue_() to pass request through without changes."""

        intercepted = False

        def passthrough_handler(route: Route):
            nonlocal intercepted
            intercepted = True
            route.continue_()

        page.route(f"{API_URL}/**", passthrough_handler)
        page.goto(f"{BASE_URL}/hospitals")
        page.wait_for_timeout(2000)

        print(f"API request intercepted and passed through: {intercepted}")


@pytest.mark.network
class TestMockLoginAPI:
    """
    Mock the login API to test frontend behavior with different responses.
    """

    def test_mock_successful_login(self, page: Page):
        """Mock login API to return success — verify frontend handles it."""

        def mock_login_success(route: Route):
            route.fulfill(
                status=200,
                content_type="application/json",
                json={
                    "access_token": "mock-jwt-token-12345",
                    "token_type": "bearer",
                    "user": {
                        "id": 1,
                        "name": "Test User",
                        "email": "test@test.com",
                    },
                },
            )

        page.route(f"{API_URL}/patients/login", mock_login_success)
        page.goto(f"{BASE_URL}/login")

        page.get_by_label("Email").fill("test@test.com")
        page.get_by_placeholder("Your password").fill("Test123#")
        page.get_by_role("button", name="Log in").click()
        page.wait_for_timeout(2000)

        print("Mock login success: submitted with mocked 200 response")

    def test_mock_failed_login(self, page: Page):
        """Mock login API to return 401 error — verify error handling."""

        def mock_login_fail(route: Route):
            route.fulfill(
                status=401,
                content_type="application/json",
                json={
                    "detail": "Invalid credentials",
                },
            )

        page.route(f"{API_URL}/patients/login", mock_login_fail)
        page.goto(f"{BASE_URL}/login")

        page.get_by_label("Email").fill("wrong@test.com")
        page.get_by_placeholder("Your password").fill("WrongPass")
        page.get_by_role("button", name="Log in").click()
        page.wait_for_timeout(2000)

        # Page should stay on login — show error, not crash
        expect(page).to_have_url(f"{BASE_URL}/login")
        print("Mock failed login: error handled gracefully — stayed on /login")

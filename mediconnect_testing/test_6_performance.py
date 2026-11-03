"""
TYPE 6 — PERFORMANCE TESTING
==============================
Measures page load times, checks that pages load within acceptable
thresholds, and verifies that no console errors appear during rendering.

Covers:
  • Landing page loads within 10 seconds
  • Login page loads within 10 seconds
  • About page loads within 10 seconds
  • Hospitals page loads within 10 seconds
  • No JavaScript console errors on key pages
  • Page title is set correctly (SEO check)
  • Multiple rapid navigations don't break the app
"""

import time
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5174"

# Maximum acceptable page load time in seconds (generous for dev server)
MAX_LOAD_TIME = 10.0


@pytest.mark.performance
class TestPageLoadTimes:
    """Verifies pages load within the acceptable time threshold."""

    def test_landing_page_load_time(self, page: Page):
        start = time.time()
        page.goto(BASE_URL, wait_until="networkidle")
        elapsed = time.time() - start

        assert elapsed < MAX_LOAD_TIME, (
            f"Landing page took {elapsed:.2f}s to load (max {MAX_LOAD_TIME}s)"
        )

    def test_login_page_load_time(self, page: Page):
        start = time.time()
        page.goto(f"{BASE_URL}/login", wait_until="networkidle")
        elapsed = time.time() - start

        assert elapsed < MAX_LOAD_TIME, (
            f"Login page took {elapsed:.2f}s to load (max {MAX_LOAD_TIME}s)"
        )

    def test_about_page_load_time(self, page: Page):
        start = time.time()
        page.goto(f"{BASE_URL}/about", wait_until="networkidle")
        elapsed = time.time() - start

        assert elapsed < MAX_LOAD_TIME, (
            f"About page took {elapsed:.2f}s to load (max {MAX_LOAD_TIME}s)"
        )

    def test_hospitals_page_load_time(self, page: Page):
        start = time.time()
        page.goto(f"{BASE_URL}/hospitals", wait_until="networkidle")
        elapsed = time.time() - start

        assert elapsed < MAX_LOAD_TIME, (
            f"Hospitals page took {elapsed:.2f}s to load (max {MAX_LOAD_TIME}s)"
        )

    def test_signup_page_load_time(self, page: Page):
        start = time.time()
        page.goto(f"{BASE_URL}/signup", wait_until="networkidle")
        elapsed = time.time() - start

        assert elapsed < MAX_LOAD_TIME, (
            f"Signup page took {elapsed:.2f}s to load (max {MAX_LOAD_TIME}s)"
        )

    def test_doctor_login_load_time(self, page: Page):
        start = time.time()
        page.goto(f"{BASE_URL}/doctor/login", wait_until="networkidle")
        elapsed = time.time() - start

        assert elapsed < MAX_LOAD_TIME, (
            f"Doctor login page took {elapsed:.2f}s to load (max {MAX_LOAD_TIME}s)"
        )


@pytest.mark.performance
class TestConsoleErrors:
    """Checks that no JavaScript errors appear in the browser console."""

    def test_landing_no_errors(self, page: Page):
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(BASE_URL, wait_until="networkidle")

        assert len(errors) == 0, f"Console errors on landing page: {errors}"

    def test_login_no_errors(self, page: Page):
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(f"{BASE_URL}/login", wait_until="networkidle")

        assert len(errors) == 0, f"Console errors on login page: {errors}"

    def test_about_no_errors(self, page: Page):
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(f"{BASE_URL}/about", wait_until="networkidle")

        assert len(errors) == 0, f"Console errors on about page: {errors}"

    def test_hospitals_no_errors(self, page: Page):
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(f"{BASE_URL}/hospitals", wait_until="networkidle")

        assert len(errors) == 0, f"Console errors on hospitals page: {errors}"


@pytest.mark.performance
class TestPageTitles:
    """Verifies that pages set their <title> correctly (important for SEO)."""

    def test_login_page_title(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        expect(page).to_have_title("Log In | MediConnect")

    def test_signup_page_title(self, page: Page):
        page.goto(f"{BASE_URL}/signup")
        expect(page).to_have_title("Sign Up | MediConnect")

    def test_about_page_title(self, page: Page):
        page.goto(f"{BASE_URL}/about")
        expect(page).to_have_title("About Us | MediConnect")

    def test_hospitals_page_title(self, page: Page):
        page.goto(f"{BASE_URL}/hospitals")
        expect(page).to_have_title("Find Hospitals | MediConnect")

    def test_404_page_title(self, page: Page):
        page.goto(f"{BASE_URL}/nonexistent-page-xyz")
        expect(page).to_have_title("Page not found | MediConnect")


@pytest.mark.performance
class TestRapidNavigation:
    """Tests that the app handles rapid page transitions gracefully."""

    def test_rapid_navigation_no_crash(self, page: Page):
        """Quickly navigating between several pages should not crash."""
        routes = ["/", "/about", "/hospitals", "/login", "/signup", "/"]
        for route in routes:
            page.goto(f"{BASE_URL}{route}")

        # After all navigations, the final page should render correctly
        expect(page.locator("h1")).to_contain_text("Find a doctor")

    def test_rapid_back_forward(self, page: Page):
        """Pressing back and forward multiple times should not crash."""
        page.goto(BASE_URL)
        page.goto(f"{BASE_URL}/about")
        page.goto(f"{BASE_URL}/hospitals")

        page.go_back()
        page.go_back()
        page.go_forward()
        page.go_forward()

        expect(page.locator("h1")).to_contain_text("Find a hospital")

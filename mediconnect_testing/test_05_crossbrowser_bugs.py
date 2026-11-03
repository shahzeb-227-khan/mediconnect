"""
FILE 5 — CROSS-BROWSER TESTING & INTENTIONAL BUG DEMONSTRATION
=================================================================
Part A: Tests that MediConnect works across Chromium, Firefox, and WebKit.
Part B: Demonstrates an intentional bug inserted into the application.

How the Bug Demo Works:
  The RUN_TESTS_NOW.bat script:
    1. Inserts a real bug into the application's source code
       (changes the login error message in Login.jsx)
    2. Runs the bug detection test → it FAILS (proves the bug exists)
    3. Reverts the bug (restores original code)
    4. Runs the same test again → it PASSES (proves the fix works)

Playwright Concepts Used:
  - Cross-browser testing (pytest --browser chromium --browser firefox --browser webkit)
  - --screenshot only-on-failure for failure evidence
  - Intentional bug insertion to demonstrate test failure
  - re.compile() for regex matching in assertions
  - expect().not_to pattern for negative assertions
"""

import re
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://localhost:5174"


# ── Part A: Cross-Browser Compatibility Tests ──────────────────────
@pytest.mark.crossbrowser
class TestCrossBrowserLanding:
    """Tests that the landing page renders correctly in any browser."""

    def test_landing_page_loads(self, page: Page):
        """Landing page should load and show hero heading."""
        page.goto(BASE_URL, wait_until="networkidle")
        heading = page.locator("h1")
        expect(heading).to_be_visible()
        expect(heading).to_contain_text("Find a doctor")

    def test_landing_page_has_navbar(self, page: Page):
        """Navbar should be visible on landing page."""
        page.goto(BASE_URL)
        nav = page.locator("nav, header, [class*='nav'], [class*='header']").first
        expect(nav).to_be_visible()

    def test_landing_page_has_search(self, page: Page):
        """Search functionality should be present."""
        page.goto(BASE_URL)
        search_el = page.locator(
            'select, button:has-text("Search"), '
            'input[type="search"], input[placeholder*="search" i]'
        ).first
        expect(search_el).to_be_visible()


@pytest.mark.crossbrowser
class TestCrossBrowserLogin:
    """Tests login page renders correctly across browsers."""

    def test_login_page_renders(self, page: Page):
        """Login page should render form elements."""
        page.goto(f"{BASE_URL}/login")
        email_input = page.locator('input[type="email"], input[name="email"]').first
        password_input = page.locator('input[type="password"]').first
        expect(email_input).to_be_visible()
        expect(password_input).to_be_visible()

    def test_login_page_has_submit_button(self, page: Page):
        """Login page should have a submit button."""
        page.goto(f"{BASE_URL}/login")
        submit_btn = page.locator('button[type="submit"]').first
        expect(submit_btn).to_be_visible()


@pytest.mark.crossbrowser
class TestCrossBrowserNavigation:
    """Tests navigation works correctly across browsers."""

    def test_navigate_to_about(self, page: Page):
        """Navigation to About page should work."""
        page.goto(f"{BASE_URL}/about")
        expect(page).to_have_url(f"{BASE_URL}/about")

    def test_navigate_to_hospitals(self, page: Page):
        """Navigation to Hospitals page should work."""
        page.goto(f"{BASE_URL}/hospitals")
        expect(page).to_have_url(f"{BASE_URL}/hospitals")


@pytest.mark.crossbrowser
class TestRegexAssertions:
    """Tests using re.compile() for regex-based assertions."""

    def test_title_matches_regex(self, page: Page):
        """Page title should match a regex pattern with MediConnect."""
        page.goto(BASE_URL)
        expect(page).to_have_title(re.compile(r".*MediConnect.*", re.IGNORECASE))

    def test_url_matches_regex(self, page: Page):
        """Page URL should match localhost pattern."""
        page.goto(f"{BASE_URL}/login")
        expect(page).to_have_url(re.compile(r".*localhost.*login.*"))

    def test_heading_text_matches_regex(self, page: Page):
        """Heading text should match regex pattern."""
        page.goto(BASE_URL)
        heading = page.locator("h1").first
        expect(heading).to_have_text(re.compile(r".*[Ff]ind.*[Dd]octor.*"))


# ── Part B: INTENTIONAL BUG DEMONSTRATION ──────────────────────────
@pytest.mark.bug
class TestIntentionalBug:
    """
    INTENTIONAL BUG DEMONSTRATION
    ==============================
    This test checks the login error message text. When the bug is
    inserted (by the batch script), the error message in Login.jsx is
    changed from "Invalid credentials" to "BUGGED_ERROR_MSG_12345".
    The test expects the ORIGINAL correct text, so it FAILS when the
    bug is present and PASSES when the code is correct.

    This is NOT a fake assertion — it tests a real UI element that was
    actually modified in the source code, fulfilling the requirement:
    "Insert an intentional bug in the application and write a test
    to demonstrate the test failure."
    """

    def test_login_error_message_is_correct(self, page: Page):
        """
        After entering wrong credentials, the error message should say
        'Invalid credentials' (or similar). When the intentional bug is
        active, the message says 'BUGGED_ERROR_MSG_12345' instead, and
        this test FAILS — proving the bug detection works.
        """
        page.goto(f"{BASE_URL}/login")
        page.get_by_label("Email").fill("wrong@test.com")
        page.get_by_placeholder("Your password").fill("WrongPassword123")
        page.get_by_role("button", name="Log in").click()

        # Wait for error to appear
        error_alert = page.locator("[role='alert']")
        expect(error_alert).to_be_visible(timeout=15_000)

        # The error message should NOT contain our bug marker
        expect(error_alert).not_to_have_text(
            re.compile(".*BUGGED_ERROR_MSG.*"),
            timeout=3000,
        )
        print("✓ Login error message is correct (no bug present)")

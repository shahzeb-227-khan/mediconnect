import re
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://localhost:5175"


# ── Cross-Browser Compatibility Tests ───────────────────────────────
@pytest.mark.crossbrowser
class TestCrossBrowserLanding:
    """
    Tests that the landing page renders correctly.
    When run with --browser firefox --browser webkit, these tests
    execute in each browser automatically.
    """

    def test_landing_page_loads(self, page: Page):
        """Landing page should load and show hero heading in any browser."""
        page.goto(BASE_URL, wait_until="networkidle")
        heading = page.locator("h1")
        expect(heading).to_be_visible()
        expect(heading).to_contain_text("Find a doctor")
        print(f"Landing page loads correctly in current browser")

    def test_landing_page_has_navbar(self, page: Page):
        """Navbar should be visible on landing page in any browser."""
        page.goto(BASE_URL)
        nav = page.locator("nav, header, [class*='nav'], [class*='header']").first
        expect(nav).to_be_visible()
        print("Navbar visible across browsers")

    def test_landing_page_has_search(self, page: Page):
        """Search functionality should be present in any browser."""
        page.goto(BASE_URL)
        # Landing page uses combobox dropdowns (city + specialization) + a Search button
        # Accept any of: a select dropdown OR a Search button OR a search-style input
        search_el = page.locator(
            'select, button[type="button"]:has-text("Search"), '
            'button:has-text("Search"), '
            'input[type="search"], input[placeholder*="search" i]'
        ).first
        expect(search_el).to_be_visible()
        print("Search UI element visible across browsers")


@pytest.mark.crossbrowser
class TestCrossBrowserLogin:
    """Tests login page renders correctly across browsers."""

    def test_login_page_renders(self, page: Page):
        """Login page should render form elements in any browser."""
        page.goto(f"{BASE_URL}/login")
        email_input = page.locator('input[type="email"], input[name="email"]').first
        password_input = page.locator('input[type="password"]').first

        expect(email_input).to_be_visible()
        expect(password_input).to_be_visible()
        print("Login form renders correctly across browsers")

    def test_login_page_has_submit_button(self, page: Page):
        """Login page should have a submit button in any browser."""
        page.goto(f"{BASE_URL}/login")
        submit_btn = page.locator('button[type="submit"]').first
        expect(submit_btn).to_be_visible()
        print("Submit button visible across browsers")


@pytest.mark.crossbrowser
class TestCrossBrowserNavigation:
    """Tests navigation works correctly across browsers."""

    def test_navigate_to_about(self, page: Page):
        """Navigation to About page should work in any browser."""
        page.goto(BASE_URL)
        page.goto(f"{BASE_URL}/about")
        expect(page).to_have_url(f"{BASE_URL}/about")
        print("About page navigation works across browsers")

    def test_navigate_to_hospitals(self, page: Page):
        """Navigation to Hospitals page should work in any browser."""
        page.goto(BASE_URL)
        page.goto(f"{BASE_URL}/hospitals")
        expect(page).to_have_url(f"{BASE_URL}/hospitals")
        print("Hospitals page navigation works across browsers")


# ── Regex Assertion Tests (re.compile) ──────────────────────────────
@pytest.mark.crossbrowser
class TestRegexAssertions:
    """Tests using re.compile() for regex-based assertions (Lab #09)."""

    def test_title_matches_regex(self, page: Page):
        """Page title should match a regex pattern with MediConnect."""
        page.goto(BASE_URL)
        # Use re.compile() for regex matching in assertions
        expect(page).to_have_title(re.compile(r".*MediConnect.*", re.IGNORECASE))
        print("Title matches regex pattern for MediConnect")

    def test_url_matches_regex(self, page: Page):
        """Page URL should match localhost pattern."""
        page.goto(f"{BASE_URL}/login")
        expect(page).to_have_url(re.compile(r".*localhost.*login.*"))
        print("URL matches regex pattern")

    def test_heading_text_matches_regex(self, page: Page):
        """Heading text should match regex pattern."""
        page.goto(BASE_URL)
        heading = page.locator("h1").first
        # Use regex to match heading text flexibly
        expect(heading).to_have_text(re.compile(r".*[Ff]ind.*[Dd]octor.*"))
        print("Heading text matches regex pattern")


# ── INTENTIONAL BUG: Deliberate Test Failures ───────────────────────
@pytest.mark.bug
class TestIntentionalBugFailures:

    def test_intentional_wrong_title(self, page: Page):
        """
        INTENTIONAL BUG: Expects wrong page title.
        This test SHOULD FAIL because the actual title contains 'MediConnect'
        but we intentionally check for 'WrongTitle_BugDemo'.
        """
        page.goto(BASE_URL)
        # BUG: Intentionally wrong expected title
        expect(page).to_have_title(
            "WrongTitle_BugDemo",
            timeout=3000,
        )

    def test_intentional_wrong_heading(self, page: Page):
        """
        INTENTIONAL BUG: Expects wrong heading text.
        This test SHOULD FAIL because the heading says 'Find a doctor'
        but we intentionally check for 'This heading does not exist'.
        """
        page.goto(BASE_URL)
        heading = page.locator("h1").first
        # BUG: Intentionally wrong expected text
        expect(heading).to_have_text(
            "This heading does not exist - BUG DEMO",
            timeout=3000,
        )

    def test_intentional_wrong_url(self, page: Page):
        """
        INTENTIONAL BUG: Expects wrong URL after navigation.
        This test SHOULD FAIL because we navigate to /login
        but intentionally check for /dashboard URL.
        """
        page.goto(f"{BASE_URL}/login")
        # BUG: Intentionally wrong expected URL
        expect(page).to_have_url(
            f"{BASE_URL}/dashboard",
            timeout=3000,
        )

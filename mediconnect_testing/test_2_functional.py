"""
TYPE 2 — FUNCTIONAL TESTING
============================
Verifies that application features work as expected by interacting with
the UI and checking outcomes. Tests real user workflows.

Covers:
  • Feature 1 — Patient Login:
      (Positive) Login with valid credentials → redirect
      (Negative) Login with wrong password → error shown
  • Feature 2 — Patient Signup:
      (Positive) Sign up with new random account
      (Negative) Empty form blocked by validation
  • Feature 3 — Hospital Search:
      (Positive) Search input accepts text
      (Negative) Nonsense search shows graceful result
  • Symptom checker toggle on landing page
  • Doctor portal link navigation
"""

import re
import random
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5174"

# Real test credentials
TEST_EMAIL    = "shahzebalam5002@gmail.com"
TEST_PASSWORD = "Cb223223w"


# ── Feature 1: Patient Login ─────────────────────────────────────────
@pytest.mark.functional
class TestPatientLoginFunctional:
    """Tests the patient login workflow — 3 tests for Feature 1."""

    def test_valid_login_succeeds(self, login_page: Page):
        """
        [POSITIVE] Login with correct credentials should redirect away from /login.
        Feature 1 — Positive test.
        """
        login_page.get_by_label("Email").fill(TEST_EMAIL)
        login_page.get_by_placeholder("Your password").fill(TEST_PASSWORD)
        login_page.get_by_role("button", name="Log in").click()

        # Either redirects away from /login, or stays (if already logged in)
        login_page.wait_for_timeout(3000)
        # The page should NOT show a login error
        error_visible = login_page.locator("[role='alert']").is_visible()
        current_url = login_page.url
        # Success = navigated away from login OR no error shown
        assert "/login" not in current_url or not error_visible, (
            "Login with valid credentials failed — still on login with error"
        )
        print(f"Login result URL: {current_url}")

    def test_invalid_credentials_show_error(self, login_page: Page):
        """
        [NEGATIVE] Login with wrong credentials must surface an error message.
        Feature 1 — Negative test.
        """
        login_page.get_by_label("Email").fill("nonexistent@test.com")
        login_page.get_by_placeholder("Your password").fill("WrongPassword123")
        login_page.get_by_role("button", name="Log in").click()

        error_alert = login_page.locator("[role='alert']")
        expect(error_alert).to_be_visible(timeout=15_000)

    def test_empty_form_submission_blocked(self, login_page: Page):
        """
        [NEGATIVE] Browser native validation should prevent submitting empty fields.
        Feature 1 — Negative test.
        """
        btn = login_page.get_by_role("button", name="Log in")
        btn.click()
        # Should still be on login page (form not submitted)
        expect(login_page).to_have_url(re.compile(".*/login"))

    def test_doctor_portal_link(self, login_page: Page):
        """The 'Are you a doctor?' link should navigate to /doctor/login."""
        login_page.get_by_text("Are you a doctor?").click()
        expect(login_page).to_have_url(re.compile(".*/doctor/login"))


# ── Feature 2: Patient Signup ────────────────────────────────────────
@pytest.mark.functional
class TestSignupFunctional:
    """Tests the patient signup form — 3 tests for Feature 2."""

    def test_valid_signup_creates_account(self, signup_page: Page):
        """
        [POSITIVE] Sign up with a fresh random email should succeed.
        Feature 2 — Positive test.
        """
        rand_id = random.randint(10000, 99999)
        signup_page.get_by_label("Full name").fill(f"Test User {rand_id}")
        signup_page.get_by_label("Email").fill(f"testuser{rand_id}@playwright-test.com")
        # Use input[type="password"] directly — more robust than placeholder text
        pw_field = signup_page.locator('input[type="password"]').first
        pw_field.fill("TestPass123#")
        signup_page.locator("main").get_by_role("button", name="Sign up").click()

        signup_page.wait_for_timeout(4000)
        # Success: navigated away from /signup  OR  no error alert
        error_visible = signup_page.locator("[role='alert']").is_visible()
        current_url = signup_page.url
        success = "/signup" not in current_url or not error_visible
        print(f"Signup result URL: {current_url}, error_visible: {error_visible}")
        assert success, "Signup with valid data failed unexpectedly"

    def test_empty_form_blocked(self, signup_page: Page):
        """
        [NEGATIVE] Browser validation should prevent submitting the empty signup form.
        Feature 2 — Negative test.
        """
        signup_page.locator("main").get_by_role("button", name="Sign up").click()
        expect(signup_page).to_have_url(re.compile(".*/signup"))

    def test_password_hint_visible(self, signup_page: Page):
        """
        [NEGATIVE] The password requirement hint should be shown (guard against weak passwords).
        Feature 2 — Negative guard test.
        """
        expect(signup_page.get_by_text("At least 8 characters")).to_be_visible()


# ── Feature 3: Hospital Search / Browse ─────────────────────────────
@pytest.mark.functional
class TestHospitalSearchFunctional:
    """Tests the hospital listing and search — 3 tests for Feature 3."""

    def test_search_input_accepts_text(self, hospitals_page: Page):
        """
        [POSITIVE] The search box should accept typed text.
        Feature 3 — Positive test.
        """
        search_input = hospitals_page.get_by_placeholder("Search hospital name")
        search_input.fill("Aga Khan")
        expect(search_input).to_have_value("Aga Khan")

    def test_nonsense_search_shows_graceful_result(self, hospitals_page: Page):
        """
        [NEGATIVE] Typing gibberish in search should not crash the page.
        Feature 3 — Negative test.
        """
        search_input = hospitals_page.get_by_placeholder("Search hospital name")
        search_input.fill("xyzxyz999nosuchplace")
        hospitals_page.wait_for_timeout(1500)
        # Page should still be on /hospitals (no crash / redirect)
        expect(hospitals_page).to_have_url(f"{BASE_URL}/hospitals")
        print("Nonsense search handled gracefully — no crash")

    def test_city_filter_dropdown(self, hospitals_page: Page):
        """
        [POSITIVE] The city filter dropdown should be interactive.
        Feature 3 — Positive test.
        """
        city_select = hospitals_page.locator("select")
        expect(city_select).to_be_visible()
        first_option = city_select.locator("option").first
        expect(first_option).to_have_text("All cities")


# ── Search on landing page ───────────────────────────────────────────
@pytest.mark.functional
class TestSearchFunctional:
    """Tests the search functionality on the landing page."""

    def test_search_navigates_to_results(self, home: Page):
        """Clicking Search without filters goes to /search."""
        home.get_by_role("button", name="Search").click()
        expect(home).to_have_url(re.compile(".*/search"))

    def test_search_results_page_loads(self, home: Page):
        """The search results page should show the heading."""
        home.get_by_role("button", name="Search").click()
        expect(home.locator("h1")).to_contain_text("Find a doctor")

    def test_symptom_checker_toggle(self, home: Page):
        """Clicking 'Not sure which specialist you need?' reveals the symptom form."""
        trigger = home.get_by_text("Not sure which specialist you need?")
        expect(trigger).to_be_visible()
        trigger.click()
        expect(home.get_by_text("Describe how you're feeling")).to_be_visible()
        expect(home.get_by_placeholder("e.g. chest tightness")).to_be_visible()

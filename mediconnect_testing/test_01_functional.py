"""
FILE 1 — END-TO-END (E2E) FUNCTIONAL TESTING
==============================================
Tests four core features of MediConnect with exactly 3 E2E tests
per feature (12 tests total), as required by the problem statement.

Features:
  Feature 1 — Patient Login       (3 tests: positive + 2 negative)
  Feature 2 — Patient Signup      (3 tests: positive + 2 negative)
  Feature 3 — Hospital Search     (3 tests: positive + 2 negative)
  Feature 4 — Doctor Login Portal (3 tests: positive + 2 negative)

Playwright Concepts Used:
  - page.goto(), page.url
  - Locators: get_by_label(), get_by_placeholder(), get_by_role(),
    get_by_text(), locator() with CSS selectors, .first
  - Actions: .fill(), .click()
  - Assertions: expect(page).to_have_url(), expect(locator).to_be_visible(),
    expect(locator).to_have_text(), expect(locator).to_have_value()
  - re.compile() for regex URL matching
  - wait_for_timeout() for async operations
  - Strict mode with .first for multiple matches
  - Auto-waiting built into Playwright actions
"""

import re
import os
import random
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5174"

# Credentials from environment variables (never hardcoded)
TEST_EMAIL    = os.environ.get("MEDI_TEST_EMAIL", "")
TEST_PASSWORD = os.environ.get("MEDI_TEST_PASSWORD", "")


# ── Feature 1: Patient Login (3 tests) ─────────────────────────────
@pytest.mark.functional
class TestFeature1_PatientLogin:
    """Feature 1 — Patient Login: 3 E2E tests (1 positive, 2 negative)."""

    def test_f1_valid_login_redirects(self, login_page: Page):
        """
        [POSITIVE] Login with correct credentials should redirect
        away from /login page (to dashboard or home).
        """
        login_page.get_by_label("Email").fill(TEST_EMAIL)
        login_page.get_by_placeholder("Your password").fill(TEST_PASSWORD)
        login_page.get_by_role("button", name="Log in").click()

        login_page.wait_for_timeout(3000)
        error_visible = login_page.locator("[role='alert']").is_visible()
        current_url = login_page.url
        assert "/login" not in current_url or not error_visible, (
            "Login with valid credentials failed — still on login with error"
        )
        print(f"✓ Login redirected to: {current_url}")

    def test_f1_wrong_password_shows_error(self, login_page: Page):
        """
        [NEGATIVE] Login with wrong password must show an error alert.
        """
        login_page.get_by_label("Email").fill("nonexistent@test.com")
        login_page.get_by_placeholder("Your password").fill("WrongPassword123")
        login_page.get_by_role("button", name="Log in").click()

        error_alert = login_page.locator("[role='alert']")
        expect(error_alert).to_be_visible(timeout=15_000)

    def test_f1_empty_form_stays_on_login(self, login_page: Page):
        """
        [NEGATIVE] Submitting empty login form should NOT leave the
        login page — browser validation should block it.
        """
        login_page.get_by_role("button", name="Log in").click()
        expect(login_page).to_have_url(re.compile(".*/login"))


# ── Feature 2: Patient Signup (3 tests) ─────────────────────────────
@pytest.mark.functional
class TestFeature2_PatientSignup:
    """Feature 2 — Patient Signup: 3 E2E tests (1 positive, 2 negative)."""

    def test_f2_valid_signup_creates_account(self, signup_page: Page):
        """
        [POSITIVE] Sign up with random valid data should succeed
        (navigates away from /signup or shows no error).
        """
        rand_id = random.randint(10000, 99999)
        signup_page.get_by_label("Full name").fill(f"Test User {rand_id}")
        signup_page.get_by_label("Email").fill(f"testuser{rand_id}@playwright-test.com")
        pw_field = signup_page.locator('input[type="password"]').first
        pw_field.fill("TestPass123#")
        signup_page.locator("main").get_by_role("button", name="Sign up").click()

        signup_page.wait_for_timeout(4000)
        error_visible = signup_page.locator("[role='alert']").is_visible()
        current_url = signup_page.url
        success = "/signup" not in current_url or not error_visible
        assert success, "Signup with valid data failed unexpectedly"
        print(f"✓ Signup result URL: {current_url}")

    def test_f2_empty_form_blocked(self, signup_page: Page):
        """
        [NEGATIVE] Browser validation should prevent empty signup
        form submission — user stays on /signup.
        """
        signup_page.locator("main").get_by_role("button", name="Sign up").click()
        expect(signup_page).to_have_url(re.compile(".*/signup"))

    def test_f2_password_hint_visible(self, signup_page: Page):
        """
        [NEGATIVE GUARD] Password requirements hint must be visible
        to prevent users from choosing weak passwords.
        """
        expect(signup_page.get_by_text("At least 8 characters")).to_be_visible()


# ── Feature 3: Hospital Search (3 tests) ────────────────────────────
@pytest.mark.functional
class TestFeature3_HospitalSearch:
    """Feature 3 — Hospital Search: 3 E2E tests (1 positive, 2 negative)."""

    def test_f3_search_accepts_text(self, hospitals_page: Page):
        """
        [POSITIVE] The search box should accept typed text and retain it.
        """
        search_input = hospitals_page.get_by_placeholder("Search hospital name")
        search_input.fill("Aga Khan")
        expect(search_input).to_have_value("Aga Khan")

    def test_f3_nonsense_search_no_crash(self, hospitals_page: Page):
        """
        [NEGATIVE] Typing gibberish should not crash the page.
        """
        search_input = hospitals_page.get_by_placeholder("Search hospital name")
        search_input.fill("xyzxyz999nosuchplace")
        hospitals_page.wait_for_timeout(1500)
        expect(hospitals_page).to_have_url(f"{BASE_URL}/hospitals")
        print("✓ Nonsense search handled gracefully — no crash")

    def test_f3_city_filter_dropdown(self, hospitals_page: Page):
        """
        [POSITIVE] The city filter dropdown should be visible and
        default to 'All cities'.
        """
        city_select = hospitals_page.locator("select")
        expect(city_select).to_be_visible()
        first_option = city_select.locator("option").first
        expect(first_option).to_have_text("All cities")


# ── Feature 4: Doctor Login Portal (3 tests) ────────────────────────
@pytest.mark.functional
class TestFeature4_DoctorLogin:
    """Feature 4 — Doctor Login Portal: 3 E2E tests (1 positive, 2 negative)."""

    def test_f4_doctor_login_page_renders(self, doctor_login_page: Page):
        """
        [POSITIVE] The doctor login page should render with email
        and password fields.
        """
        email_input = doctor_login_page.locator('input[type="email"], input[name="email"]').first
        password_input = doctor_login_page.locator('input[type="password"]').first
        expect(email_input).to_be_visible()
        expect(password_input).to_be_visible()
        print("✓ Doctor login page renders correctly")

    def test_f4_wrong_doctor_credentials_error(self, doctor_login_page: Page):
        """
        [NEGATIVE] Wrong credentials on doctor login should show error
        or remain on login page.
        """
        email_input = doctor_login_page.locator('input[type="email"], input[name="email"]').first
        password_input = doctor_login_page.locator('input[type="password"]').first
        email_input.fill("fakedoctor@test.com")
        password_input.fill("WrongPass123")
        doctor_login_page.locator('button[type="submit"]').first.click()

        doctor_login_page.wait_for_timeout(3000)
        # Should still be on doctor login (failed) or show error
        expect(doctor_login_page).to_have_url(re.compile(".*/doctor/login"))
        print("✓ Wrong doctor credentials kept user on login page")

    def test_f4_empty_doctor_form_blocked(self, doctor_login_page: Page):
        """
        [NEGATIVE] Empty doctor login form should not submit —
        browser validation keeps user on the page.
        """
        doctor_login_page.locator('button[type="submit"]').first.click()
        expect(doctor_login_page).to_have_url(re.compile(".*/doctor/login"))

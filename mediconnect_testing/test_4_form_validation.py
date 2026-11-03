"""
TYPE 4 — FORM VALIDATION TESTING
==================================
Verifies that form inputs enforce the correct validation rules:
required fields, email format, password constraints, and field types.

Covers:
  • Patient login form: required fields, email format
  • Patient signup form: required fields, password rules
  • Doctor login form: required fields
  • Hospital search: input behavior
  • Symptom checker: required field
"""

import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5174"


@pytest.mark.form_validation
class TestPatientLoginValidation:
    """Validates the patient login form enforces correct constraints."""

    def test_email_required(self, login_page: Page):
        """The email field must be marked as required."""
        email_input = login_page.get_by_label("Email")
        expect(email_input).to_have_attribute("required", "")

    def test_password_required(self, login_page: Page):
        """The password field must be marked as required."""
        password_input = login_page.get_by_label("Password")
        expect(password_input).to_have_attribute("required", "")

    def test_email_type_attribute(self, login_page: Page):
        """The email field should have type='email' for browser validation."""
        email_input = login_page.get_by_label("Email")
        expect(email_input).to_have_attribute("type", "email")

    def test_email_autocomplete(self, login_page: Page):
        """The email field should have correct autocomplete for autofill."""
        email_input = login_page.get_by_label("Email")
        expect(email_input).to_have_attribute("autocomplete", "email")

    def test_password_autocomplete(self, login_page: Page):
        """The password field should have autocomplete='current-password'."""
        password_input = login_page.get_by_label("Password")
        expect(password_input).to_have_attribute("autocomplete", "current-password")

    def test_empty_email_prevents_submit(self, login_page: Page):
        """Submitting with empty email should not navigate away."""
        login_page.get_by_label("Password").fill("SomePassword123")
        login_page.get_by_role("button", name="Log in").click()
        # Still on login — native validation blocked the submit
        expect(login_page).to_have_url(re.compile(".*/login"))

    def test_empty_password_prevents_submit(self, login_page: Page):
        """Submitting with empty password should not navigate away."""
        login_page.get_by_label("Email").fill("test@example.com")
        login_page.get_by_role("button", name="Log in").click()
        expect(login_page).to_have_url(re.compile(".*/login"))

    def test_invalid_email_format(self, login_page: Page):
        """Entering a non-email string should trigger browser validation."""
        login_page.get_by_label("Email").fill("not-an-email")
        login_page.get_by_label("Password").fill("SomePassword123")
        login_page.get_by_role("button", name="Log in").click()
        # Still on login because browser rejected the invalid email
        expect(login_page).to_have_url(re.compile(".*/login"))


@pytest.mark.form_validation
class TestPatientSignupValidation:
    """Validates the patient signup form fields and constraints."""

    def test_name_required(self, signup_page: Page):
        """The full name field must be required."""
        name_input = signup_page.get_by_label("Full name")
        expect(name_input).to_have_attribute("required", "")

    def test_email_required(self, signup_page: Page):
        """The email field must be required."""
        email_input = signup_page.get_by_label("Email")
        expect(email_input).to_have_attribute("required", "")

    def test_email_type(self, signup_page: Page):
        """The email field should be type='email'."""
        email_input = signup_page.get_by_label("Email")
        expect(email_input).to_have_attribute("type", "email")

    def test_password_required(self, signup_page: Page):
        """The password field must be required."""
        password_input = signup_page.get_by_label("Password")
        expect(password_input).to_have_attribute("required", "")

    def test_password_type(self, signup_page: Page):
        """The password field should be type='password' to mask input."""
        password_input = signup_page.get_by_label("Password")
        expect(password_input).to_have_attribute("type", "password")

    def test_phone_optional(self, signup_page: Page):
        """The phone field should NOT be required."""
        phone_input = signup_page.get_by_label("Phone number (optional)")
        # It should either not have 'required' or have required=false
        expect(phone_input).not_to_have_attribute("required", "")

    def test_password_hint_displayed(self, signup_page: Page):
        """The password requirement hint text must be visible."""
        expect(signup_page.get_by_text("At least 8 characters, one number, one uppercase letter")).to_be_visible()

    def test_submit_without_name_blocked(self, signup_page: Page):
        """Submitting without a name should be blocked by browser validation."""
        signup_page.get_by_label("Email").fill("test@example.com")
        signup_page.get_by_label("Password").fill("Test1234")
        signup_page.get_by_role("button", name="Sign up").click()
        expect(signup_page).to_have_url(re.compile(".*/signup"))


@pytest.mark.form_validation
class TestDoctorLoginValidation:
    """Validates the doctor login form fields."""

    def test_email_required(self, doctor_login_page: Page):
        """Doctor login email field must be required."""
        email_input = doctor_login_page.get_by_label("Email")
        expect(email_input).to_have_attribute("required", "")

    def test_password_required(self, doctor_login_page: Page):
        """Doctor login password field must be required."""
        password_input = doctor_login_page.get_by_label("Password")
        expect(password_input).to_have_attribute("required", "")

    def test_email_type(self, doctor_login_page: Page):
        """Doctor login email field should be type='email'."""
        email_input = doctor_login_page.get_by_label("Email")
        expect(email_input).to_have_attribute("type", "email")


@pytest.mark.form_validation
class TestHospitalSearchValidation:
    """Validates the hospital search input behavior."""

    def test_search_placeholder(self, hospitals_page: Page):
        """Search input must have the correct placeholder."""
        search = hospitals_page.get_by_placeholder("Search hospital name")
        expect(search).to_be_visible()

    def test_search_clears_on_select_all_delete(self, hospitals_page: Page):
        """Typing then clearing the search input should work."""
        search = hospitals_page.get_by_placeholder("Search hospital name")
        search.fill("Test Hospital")
        expect(search).to_have_value("Test Hospital")
        search.fill("")
        expect(search).to_have_value("")


@pytest.mark.form_validation
class TestSymptomCheckerValidation:
    """Validates the symptom checker form on the landing page."""

    def test_textarea_required(self, home: Page):
        """The symptom textarea should be required when visible."""
        home.get_by_text("Not sure which specialist you need?").click()
        textarea = home.get_by_placeholder("e.g. chest tightness")
        expect(textarea).to_have_attribute("required", "")

    def test_empty_symptom_blocked(self, home: Page):
        """Submitting an empty symptom form should be blocked."""
        home.get_by_text("Not sure which specialist you need?").click()
        home.get_by_role("button", name="Suggest a specialist").click()
        # Still on home page, form not submitted
        expect(home).to_have_url(f"{BASE_URL}/")

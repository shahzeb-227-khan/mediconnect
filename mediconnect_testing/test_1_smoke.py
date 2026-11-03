"""
TYPE 1 — SMOKE TESTING
=======================
Quick, high-level checks that the most important pages load and display
their core elements. If any of these fail, the app is fundamentally broken.

Covers:
  • Landing page renders with hero heading and search form
  • Patient login page renders with email/password fields
  • Patient signup page renders with all required fields
  • About page renders with main sections
  • Hospitals list page renders with heading
  • Doctor login page renders correctly
  • 404 page renders for unknown routes
"""

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5174"


@pytest.mark.smoke
class TestLandingPageSmoke:
    """The landing page is the entry point — it must render its hero and search."""

    def test_hero_heading_visible(self, home: Page):
        heading = home.locator("h1")
        expect(heading).to_contain_text("Find a doctor you can actually trust")

    def test_search_form_present(self, home: Page):
        # The search form has city and specialization selects + a Search button
        expect(home.locator("select").first).to_be_visible()
        expect(home.get_by_role("button", name="Search")).to_be_visible()

    def test_navbar_brand_visible(self, home: Page):
        expect(home.get_by_text("MediConnect")).to_be_visible()

    def test_feature_cards_visible(self, home: Page):
        expect(home.get_by_text("Real reviews only")).to_be_visible()
        expect(home.get_by_text("Verified healthcare professionals")).to_be_visible()
        expect(home.get_by_text("Easy token-based booking")).to_be_visible()


@pytest.mark.smoke
class TestPatientLoginSmoke:
    """The login page must show its form fields."""

    def test_login_heading(self, login_page: Page):
        expect(login_page.get_by_text("Welcome back")).to_be_visible()

    def test_email_field_present(self, login_page: Page):
        expect(login_page.get_by_label("Email")).to_be_visible()

    def test_password_field_present(self, login_page: Page):
        expect(login_page.get_by_label("Password")).to_be_visible()

    def test_login_button_present(self, login_page: Page):
        expect(login_page.get_by_role("button", name="Log in")).to_be_visible()

    def test_signup_link_present(self, login_page: Page):
        expect(login_page.get_by_role("link", name="Create an account")).to_be_visible()

    def test_forgot_password_link(self, login_page: Page):
        expect(login_page.get_by_role("link", name="Forgot password?")).to_be_visible()


@pytest.mark.smoke
class TestPatientSignupSmoke:
    """The signup page must show all required registration fields."""

    def test_signup_heading(self, signup_page: Page):
        expect(signup_page.get_by_text("Create your account")).to_be_visible()

    def test_name_field(self, signup_page: Page):
        expect(signup_page.get_by_label("Full name")).to_be_visible()

    def test_email_field(self, signup_page: Page):
        expect(signup_page.get_by_label("Email")).to_be_visible()

    def test_password_field(self, signup_page: Page):
        expect(signup_page.get_by_label("Password")).to_be_visible()

    def test_submit_button(self, signup_page: Page):
        expect(signup_page.get_by_role("button", name="Sign up")).to_be_visible()


@pytest.mark.smoke
class TestAboutPageSmoke:
    """About page must render the hero and pillar sections."""

    def test_hero_heading(self, about_page: Page):
        expect(about_page.locator("h1")).to_contain_text("Healthcare in Pakistan")

    def test_pillars_section(self, about_page: Page):
        expect(about_page.get_by_text("What we stand for")).to_be_visible()

    def test_how_it_works_section(self, about_page: Page):
        expect(about_page.get_by_text("How it works")).to_be_visible()


@pytest.mark.smoke
class TestHospitalsPageSmoke:
    """Hospitals listing page must show its heading and search controls."""

    def test_heading(self, hospitals_page: Page):
        expect(hospitals_page.locator("h1")).to_contain_text("Find a hospital")

    def test_search_input(self, hospitals_page: Page):
        expect(hospitals_page.get_by_placeholder("Search hospital name")).to_be_visible()


@pytest.mark.smoke
class TestDoctorLoginSmoke:
    """Doctor login page must render separately from patient login."""

    def test_doctor_login_heading(self, doctor_login_page: Page):
        expect(doctor_login_page.get_by_text("Welcome back")).to_be_visible()

    def test_doctor_email_field(self, doctor_login_page: Page):
        expect(doctor_login_page.get_by_label("Email")).to_be_visible()


@pytest.mark.smoke
class TestNotFoundPageSmoke:
    """Visiting a non-existent route must show the 404 page."""

    def test_404_page(self, page: Page):
        page.goto(f"{BASE_URL}/this-page-does-not-exist-xyz")
        expect(page.get_by_text("Page not found")).to_be_visible()
        expect(page.get_by_role("link", name="Back to homepage")).to_be_visible()

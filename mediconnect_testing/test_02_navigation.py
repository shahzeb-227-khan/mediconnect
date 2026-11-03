"""
FILE 2 — NAVIGATION & ROUTING TESTS
=====================================
Verifies that all links, routes, and page transitions work correctly.
These are support tests that ensure the React Router setup is sound.

Playwright Concepts Used:
  - page.goto(), page.go_back(), page.go_forward()
  - get_by_role("banner") to scope to navbar
  - get_by_role("link", name=...) for accessible link selection
  - expect(page).to_have_url() with re.compile() for regex matching
  - Browser history navigation (go_back, go_forward)
  - wait_until="networkidle" for full page load
"""

import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5174"


@pytest.mark.navigation
class TestNavbarNavigation:
    """Tests that navbar links route to the correct pages."""

    def test_home_link(self, about_page: Page):
        """Clicking 'Home' in the navbar navigates to /."""
        about_page.get_by_role("banner").get_by_role("link", name="Home", exact=True).click()
        expect(about_page).to_have_url(f"{BASE_URL}/")

    def test_hospitals_link(self, home: Page):
        """Clicking 'Find Hospitals' navigates to /hospitals."""
        home.get_by_role("banner").get_by_role("link", name="Find Hospitals").click()
        expect(home).to_have_url(f"{BASE_URL}/hospitals")

    def test_about_link(self, home: Page):
        """Clicking 'About Us' navigates to /about."""
        home.get_by_role("banner").get_by_role("link", name="About Us").click()
        expect(home).to_have_url(f"{BASE_URL}/about")

    def test_login_link(self, home: Page):
        """Clicking 'Log in' navigates to /login."""
        home.get_by_role("banner").get_by_role("link", name="Log in").click()
        expect(home).to_have_url(f"{BASE_URL}/login")

    def test_signup_button(self, home: Page):
        """Clicking 'Sign up' navigates to /signup."""
        home.get_by_role("button", name="Sign up").click()
        expect(home).to_have_url(f"{BASE_URL}/signup")


@pytest.mark.navigation
class TestCrossLinkNavigation:
    """Tests links that cross between pages (login ↔ signup)."""

    def test_login_to_signup(self, login_page: Page):
        """The 'Create an account' link on login goes to /signup."""
        login_page.get_by_role("main").get_by_role("link", name="Create an account").click()
        expect(login_page).to_have_url(f"{BASE_URL}/signup")

    def test_signup_to_login(self, signup_page: Page):
        """The 'Log in' link on signup goes to /login."""
        signup_page.get_by_role("main").get_by_role("link", name="Log in").click()
        expect(signup_page).to_have_url(f"{BASE_URL}/login")


@pytest.mark.navigation
class TestProtectedRouteRedirects:
    """Tests that protected pages redirect unauthenticated users."""

    def test_my_appointments_redirects(self, page: Page):
        """Visiting /my-appointments without login should redirect to /login."""
        page.goto(f"{BASE_URL}/my-appointments")
        expect(page).to_have_url(re.compile(".*/login"))

    def test_profile_redirects(self, page: Page):
        """Visiting /profile without login should redirect to /login."""
        page.goto(f"{BASE_URL}/profile")
        expect(page).to_have_url(re.compile(".*/login"))


@pytest.mark.navigation
class TestBrowserHistoryNavigation:
    """Tests that browser back/forward work with SPA navigation."""

    def test_back_button(self, home: Page):
        """Navigating forward then pressing back returns to the original page."""
        home.goto(f"{BASE_URL}/about")
        expect(home).to_have_url(f"{BASE_URL}/about")
        home.go_back()
        expect(home).to_have_url(f"{BASE_URL}/")

    def test_forward_button(self, home: Page):
        """After going back, forward returns to the page we came from."""
        home.goto(f"{BASE_URL}/about")
        home.go_back()
        expect(home).to_have_url(f"{BASE_URL}/")
        home.go_forward()
        expect(home).to_have_url(f"{BASE_URL}/about")

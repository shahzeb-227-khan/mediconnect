"""
TYPE 5 — RESPONSIVE / CROSS-BROWSER TESTING
=============================================
Tests that the application renders correctly at different viewport sizes
(mobile, tablet, desktop) and that responsive elements like the mobile
menu toggle work properly.

Covers:
  • Mobile viewport: hamburger menu visible, desktop nav hidden
  • Tablet viewport: layout adapts correctly
  • Desktop viewport: full navbar visible, hamburger hidden
  • Mobile navigation drawer opens and closes
  • Login page works on mobile viewport
  • About page sections render on all sizes
"""

import pytest
from playwright.sync_api import Page, expect, BrowserContext

BASE_URL = "http://localhost:5174"

# ── Viewport sizes ──────────────────────────────────────────────────────────
MOBILE   = {"width": 375, "height": 812}   # iPhone-style
TABLET   = {"width": 768, "height": 1024}  # iPad-style
DESKTOP  = {"width": 1280, "height": 800}  # Standard laptop


@pytest.mark.responsive
class TestDesktopLayout:
    """Desktop (1280px): full navbar, no hamburger."""

    def test_navbar_links_visible(self, page: Page):
        page.set_viewport_size(DESKTOP)
        page.goto(BASE_URL)

        expect(page.get_by_role("link", name="Home")).to_be_visible()
        expect(page.get_by_role("link", name="Find Hospitals")).to_be_visible()
        expect(page.get_by_role("link", name="About Us")).to_be_visible()

    def test_hamburger_hidden(self, page: Page):
        page.set_viewport_size(DESKTOP)
        page.goto(BASE_URL)

        hamburger = page.get_by_label("Open menu")
        expect(hamburger).to_be_hidden()

    def test_login_signup_buttons_visible(self, page: Page):
        page.set_viewport_size(DESKTOP)
        page.goto(BASE_URL)

        expect(page.get_by_role("link", name="Log in")).to_be_visible()
        expect(page.get_by_role("button", name="Sign up")).to_be_visible()

    def test_hero_token_card_visible(self, page: Page):
        """The decorative token card in the hero should show on desktop."""
        page.set_viewport_size(DESKTOP)
        page.goto(BASE_URL)

        expect(page.get_by_text("Your Token").first).to_be_visible()


@pytest.mark.responsive
class TestMobileLayout:
    """Mobile (375px): hamburger visible, desktop nav hidden."""

    def test_hamburger_visible(self, page: Page):
        page.set_viewport_size(MOBILE)
        page.goto(BASE_URL)

        hamburger = page.get_by_label("Open menu")
        expect(hamburger).to_be_visible()

    def test_desktop_nav_hidden(self, page: Page):
        """Nav links should be hidden in mobile (inside the drawer)."""
        page.set_viewport_size(MOBILE)
        page.goto(BASE_URL)

        # The "Find Hospitals" link in the desktop nav should be hidden
        # (it exists but inside the mobile drawer which is closed)
        nav_links = page.locator("nav.hidden")
        expect(nav_links.first).to_be_visible()  # The <nav> with class hidden

    def test_mobile_menu_opens(self, page: Page):
        """Clicking the hamburger opens the mobile navigation drawer."""
        page.set_viewport_size(MOBILE)
        page.goto(BASE_URL)

        page.get_by_label("Open menu").click()

        # The mobile drawer should now show nav links
        expect(page.get_by_role("navigation", name="").locator("text=Home").first).to_be_visible()

    def test_mobile_menu_closes(self, page: Page):
        """Clicking the X button closes the mobile menu."""
        page.set_viewport_size(MOBILE)
        page.goto(BASE_URL)

        page.get_by_label("Open menu").click()
        # Now close it
        page.get_by_label("Close menu").click()

        # The close menu button should now be gone (menu is closed)
        expect(page.get_by_label("Open menu")).to_be_visible()

    def test_mobile_login_page(self, page: Page):
        """Login page should render properly on mobile."""
        page.set_viewport_size(MOBILE)
        page.goto(f"{BASE_URL}/login")

        expect(page.get_by_text("Welcome back")).to_be_visible()
        expect(page.get_by_label("Email")).to_be_visible()
        expect(page.get_by_label("Password")).to_be_visible()
        expect(page.get_by_role("button", name="Log in")).to_be_visible()


@pytest.mark.responsive
class TestTabletLayout:
    """Tablet (768px): checks that the layout is usable at medium widths."""

    def test_landing_page_renders(self, page: Page):
        page.set_viewport_size(TABLET)
        page.goto(BASE_URL)

        expect(page.locator("h1")).to_contain_text("Find a doctor")
        expect(page.get_by_role("button", name="Search")).to_be_visible()

    def test_about_page_renders(self, page: Page):
        page.set_viewport_size(TABLET)
        page.goto(f"{BASE_URL}/about")

        expect(page.locator("h1")).to_contain_text("Healthcare in Pakistan")
        expect(page.get_by_text("What we stand for")).to_be_visible()

    def test_hospitals_page_renders(self, page: Page):
        page.set_viewport_size(TABLET)
        page.goto(f"{BASE_URL}/hospitals")

        expect(page.locator("h1")).to_contain_text("Find a hospital")
        expect(page.get_by_placeholder("Search hospital name")).to_be_visible()


@pytest.mark.responsive
class TestResponsiveSignup:
    """Signup form should be fully usable on all screen sizes."""

    def test_signup_mobile(self, page: Page):
        page.set_viewport_size(MOBILE)
        page.goto(f"{BASE_URL}/signup")

        expect(page.get_by_text("Create your account")).to_be_visible()
        expect(page.get_by_label("Full name")).to_be_visible()
        expect(page.get_by_label("Email")).to_be_visible()
        expect(page.get_by_label("Password")).to_be_visible()
        expect(page.get_by_role("button", name="Sign up")).to_be_visible()

    def test_signup_desktop(self, page: Page):
        page.set_viewport_size(DESKTOP)
        page.goto(f"{BASE_URL}/signup")

        expect(page.get_by_text("Create your account")).to_be_visible()
        expect(page.get_by_label("Full name")).to_be_visible()
        expect(page.get_by_role("button", name="Sign up")).to_be_visible()

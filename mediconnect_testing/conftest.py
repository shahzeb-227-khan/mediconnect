"""
Shared fixtures and configuration for MediConnect Playwright tests.
Provides page fixtures for all main routes and API context fixture.

Playwright Concepts Used:
  - @pytest.fixture for shared test fixtures
  - page fixture from pytest-playwright plugin
  - playwright fixture for APIRequestContext
  - Base URL configuration
  - Timeout configuration
  - yield and fixture lifecycle
  - expect.set_options() for global assertion timeout
"""

import pytest
from playwright.sync_api import Page, Playwright, APIRequestContext, expect


# ── Configuration ───────────────────────────────────────────────────
BASE_URL = "http://localhost:5174"
API_URL  = "http://localhost:8001"


# ── Global timeout setup (autouse=True — applies to every test) ──────
@pytest.fixture(autouse=True)
def setup_timeouts(page: Page):
    """Configure timeouts for every test automatically."""
    page.set_default_navigation_timeout(90_000)
    page.set_default_timeout(60_000)
    expect.set_options(timeout=15_000)
    yield


# ── Shared Page Fixtures ────────────────────────────────────────────
@pytest.fixture
def home(page: Page) -> Page:
    """Navigate to the landing / home page."""
    page.goto(BASE_URL)
    return page


@pytest.fixture
def login_page(page: Page) -> Page:
    """Navigate to the patient login page."""
    page.goto(f"{BASE_URL}/login")
    return page


@pytest.fixture
def signup_page(page: Page) -> Page:
    """Navigate to the patient signup page."""
    page.goto(f"{BASE_URL}/signup")
    return page


@pytest.fixture
def hospitals_page(page: Page) -> Page:
    """Navigate to the hospitals listing page."""
    page.goto(f"{BASE_URL}/hospitals")
    return page


@pytest.fixture
def about_page(page: Page) -> Page:
    """Navigate to the About page."""
    page.goto(f"{BASE_URL}/about")
    return page


@pytest.fixture
def doctor_login_page(page: Page) -> Page:
    """Navigate to the doctor login page."""
    page.goto(f"{BASE_URL}/doctor/login")
    return page


# ── API Request Context Fixture ─────────────────────────────────────
@pytest.fixture
def api_context(playwright: Playwright) -> APIRequestContext:
    """
    API request context with base URL and JSON headers.
    Uses yield for proper lifecycle management (Lab #12 Part C).
    """
    context = playwright.request.new_context(
        base_url=API_URL,
        extra_http_headers={"Content-Type": "application/json"},
    )
    yield context
    context.dispose()

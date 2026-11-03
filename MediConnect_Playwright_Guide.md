# MediConnect Playwright Test Suite — Quick-Start Guide

**CEP Submission — Software Testing and Strategies**
Muhammad Shahzeb Alam (SE-23055) & Muneeb Asghar (SE-23082)
NED University of Engineering & Technology | Fall 2026
Instructor: Engr. Tooba Siddiqui

---

## What's in the ZIP

```
mediconnect_testing/
├── conftest.py                 # Fixtures and shared setup
├── pytest.ini                  # Markers, default CLI flags
├── test_01_functional.py       # TC-01 to TC-12  (4 features × 3 tests)
├── test_02_navigation.py       # TC-13 to TC-23  (navigation & routing)
├── test_03_api.py              # TC-24 to TC-34  (real CRUD API tests)
├── test_04_network_mocking.py  # TC-35 to TC-41  (route interception)
├── test_05_crossbrowser_bugs.py # TC-42 to TC-52 (cross-browser + bug demo)
├── RUN_TESTS_NOW.bat           # 8-step full run (Chromium + Firefox + WebKit)
└── RUN_DEMO_HEADED.bat         # Headed demo (browser visible, slow-mo)
```

**Total: 52 test cases.**  51 pass normally; TC-52 is the bug-detection test
that intentionally fails when the bug is active and passes when the code is correct.

---

## Prerequisites

### 1 — Python & pip (3.9+)

```bash
python --version   # must be 3.9 or higher
```

### 2 — Install Python packages

```bash
pip install pytest pytest-playwright pytest-html
playwright install chromium firefox webkit
```

### 3 — MediConnect must be running

| Service  | Command (from project root)       | URL                    |
|----------|-----------------------------------|------------------------|
| Backend  | `cd backend && uvicorn main:app --reload` | http://localhost:8000 |
| Frontend | `cd frontend && npm run dev`      | http://localhost:5175  |

> **Tip:** Start Docker Desktop first if the backend uses PostgreSQL.

### 4 — Set test credentials (for login tests)

```bat
REM Windows CMD
set MEDI_TEST_EMAIL=your_registered_email@example.com
set MEDI_TEST_PASSWORD=your_password
```

```bash
# Linux / macOS
export MEDI_TEST_EMAIL=your_registered_email@example.com
export MEDI_TEST_PASSWORD=your_password
```

If you skip this step, TC-01 (valid login) will likely fail — all other tests are credential-independent.

---

## Running the Tests

### Option A — Double-click (Windows, recommended for submission demo)

1. Open a Command Prompt.
2. Set `MEDI_TEST_EMAIL` and `MEDI_TEST_PASSWORD` (see above).
3. Double-click **`RUN_TESTS_NOW.bat`**.

The batch file runs 8 steps automatically:

| Step | What happens |
|------|--------------|
| 1 | Install deps + browsers |
| 2 | Run **all 52 tests** on Chromium |
| 3 | Run cross-browser tests on **Firefox** |
| 4 | Run cross-browser tests on **WebKit** |
| 5 | **Insert bug** into `Login.jsx` (PowerShell string-replace) |
| 6 | Run bug test → it **FAILS** (bug detected!) |
| 7 | **Revert** `Login.jsx` from backup |
| 8 | Run bug test again → it **PASSES** |

Results land in `results\`.

### Option B — Headed demo (browser visible)

Double-click **`RUN_DEMO_HEADED.bat`** — the browser opens and runs each feature in slow motion so you can narrate for the instructor.

### Option C — Manual pytest commands

```bash
# All tests, Chromium
python -m pytest -v

# Specific file
python -m pytest test_01_functional.py -v

# Specific test class
python -m pytest test_01_functional.py::TestFeature2_PatientSignup -v

# By marker
python -m pytest -m api -v
python -m pytest -m "functional or navigation" -v

# Firefox
python -m pytest test_05_crossbrowser_bugs.py --browser firefox -v

# WebKit
python -m pytest test_05_crossbrowser_bugs.py --browser webkit -v

# Headed + slow-motion
python -m pytest test_04_network_mocking.py --headed --slowmo 800 -v
```

---

## Test Files — What Each Does

### test_01_functional.py — 4 Features × 3 Tests (TC-01 to TC-12)

| Class | Feature | Tests |
|-------|---------|-------|
| `TestFeature1_PatientLogin` | Patient Login | Valid login redirects, wrong password shows error, empty form blocked |
| `TestFeature2_PatientSignup` | Patient Signup | Valid signup, empty form blocked, password hint visible |
| `TestFeature3_HospitalSearch` | Hospital Search | Text input retained, nonsense query no crash, city dropdown exists |
| `TestFeature4_DoctorLogin` | Doctor Login | Page renders, wrong credentials error, empty form blocked |

### test_02_navigation.py — Navigation & Routing (TC-13 to TC-23)

- Navbar links (Home, Hospitals, About, Login, Sign Up)
- Cross-link navigation (Login ↔ Signup)
- Protected route redirects (`/my-appointments`, `/profile` → `/login`)
- Browser back/forward button behavior

### test_03_api.py — Real CRUD API Tests (TC-24 to TC-34)

Uses `playwright.request.new_context` (HTTP client, no browser):

| CRUD | What's tested |
|------|---------------|
| Create | POST /auth/signup (valid + missing fields) |
| Read | GET /hospitals (all, single, 404, query string) |
| Update | POST /auth/login (valid + invalid), PUT /patients/profile without auth |
| Delete | Nonexistent resource, DELETE appointment without auth |

### test_04_network_mocking.py — Network Interception (TC-35 to TC-41)

Playwright's `page.route()`:
- Mock empty hospital list → verify UI renders gracefully
- Mock 500 error response → verify error state
- Intercept + modify API response in-flight (`route.fetch()` + `route.fulfill()`)
- Block image requests (`route.abort()`)
- Let request pass through unchanged (`route.continue_()`)
- Mock successful / failed login via API mocking

### test_05_crossbrowser_bugs.py — Cross-Browser + Bug Demo (TC-42 to TC-52)

- Landing page, navbar, search — run on Chromium / Firefox / WebKit
- Regex assertions (`expect().to_have_title(re.compile(...))`)
- **TC-52 (Intentional Bug):** asserts the error alert does NOT contain `BUGGED_ERROR_MSG` — fails when bug is active, passes when code is correct

---

## Intentional Bug Demonstration

The test suite demonstrates a real, reversible source-code bug:

```
Original:  setError(extractErrorMessage(err))
Bugged:    setError("BUGGED_ERROR_MSG_12345")
```

**Why this works:** Vite hot-reloads `Login.jsx` within seconds of the file change, so no server restart is needed.  TC-52 then triggers a bad login and checks the error message — passing when the real error message appears, failing when the hardcoded bug string appears.

`RUN_TESTS_NOW.bat` steps 5–8 handle the full cycle automatically.

To run just the bug demo manually:

```bat
REM 1. Backup and insert bug
copy /Y ..\frontend\src\pages\patient\Login.jsx ..\frontend\src\pages\patient\Login.jsx.bak
powershell -Command "(Get-Content '..\frontend\src\pages\patient\Login.jsx') -replace 'setError\(extractErrorMessage\(err\)\)', 'setError(\"BUGGED_ERROR_MSG_12345\")' | Set-Content '..\frontend\src\pages\patient\Login.jsx'"
timeout /t 5 /nobreak

REM 2. Run bug test — expect FAIL
python -m pytest test_05_crossbrowser_bugs.py::TestIntentionalBug -v --screenshot on

REM 3. Revert
copy /Y ..\frontend\src\pages\patient\Login.jsx.bak ..\frontend\src\pages\patient\Login.jsx
timeout /t 5 /nobreak

REM 4. Run bug test — expect PASS
python -m pytest test_05_crossbrowser_bugs.py::TestIntentionalBug -v
```

---

## Output Files

| File | Contents |
|------|----------|
| `test_report.html` | Self-contained HTML report (screenshots on failure) |
| `results\chromium_all.txt` | All 52 tests on Chromium |
| `results\firefox_crossbrowser.txt` | Cross-browser subset on Firefox |
| `results\webkit_crossbrowser.txt` | Cross-browser subset on WebKit |
| `results\bug_test_FAIL.txt` | Bug test output when bug is active |
| `results\bug_test_PASS.txt` | Bug test output after bug is reverted |
| `screenshots\` | Failure screenshots (auto-saved) |

---

## Playwright Features Used

| Feature | Where |
|---------|-------|
| `page.goto()` + fixtures | `conftest.py` — every test |
| `get_by_role()`, `get_by_placeholder()` | `test_01`, `test_02` |
| `locator().first`, banner scoping | `test_02` — strict mode fix |
| `expect()` auto-retry assertions | All files |
| `expect().to_have_title(re.compile(...))` | `test_05` |
| `page.route()` — mock / abort / continue / fetch+modify | `test_04` |
| `playwright.request.new_context()` | `test_03` — API tests |
| `page.go_back()` / `page.go_forward()` | `test_02` |
| `--browser firefox/webkit` | `test_05`, `RUN_TESTS_NOW.bat` |
| `--headed --slowmo` | `RUN_DEMO_HEADED.bat` |
| `--screenshot only-on-failure` | `pytest.ini` |

---

## Common Issues

| Problem | Fix |
|---------|-----|
| `Error: connect ECONNREFUSED localhost:5175` | Start the Vite dev server: `cd frontend && npm run dev` |
| `Error: connect ECONNREFUSED localhost:8000` | Start the FastAPI backend; check Docker is running |
| Login test fails with empty credentials warning | Set `MEDI_TEST_EMAIL` and `MEDI_TEST_PASSWORD` env vars |
| `StrictModeViolation` on navbar | Already scoped to `page.get_by_role('banner')` in conftest |
| Firefox / WebKit not installed | Run `playwright install firefox webkit` |
| Bug test always passes (step 6) | Check that Vite is running with HMR; increase `timeout /t 5` to `timeout /t 10` |

---

*Generated for CEP submission — NED University, Fall 2026.*

@echo off
echo ================================================
echo  MediConnect Playwright Test Suite
echo  CEP — All Test Types
echo ================================================

call venv\Scripts\activate

echo.
echo [1/11] Installing dependencies...
pip install axe-playwright-python pytest-html --quiet
playwright install firefox --quiet

echo.
echo [2/11] TYPE 1 — Smoke Tests
python -m pytest test_1_smoke.py -v --tb=short 2>&1 | tee results\smoke.txt

echo.
echo [3/11] TYPE 2 — Functional Tests
python -m pytest test_2_functional.py -v --tb=short 2>&1 | tee results\functional.txt

echo.
echo [4/11] TYPE 3 — Navigation Tests
python -m pytest test_3_navigation.py -v --tb=short 2>&1 | tee results\navigation.txt

echo.
echo [5/11] TYPE 4 — Form Validation Tests
python -m pytest test_4_form_validation.py -v --tb=short 2>&1 | tee results\form_validation.txt

echo.
echo [6/11] TYPE 5 — Responsive Tests
python -m pytest test_5_responsive.py -v --tb=short 2>&1 | tee results\responsive.txt

echo.
echo [7/11] TYPE 6 — Performance Tests
python -m pytest test_6_performance.py -v --tb=short 2>&1 | tee results\performance.txt

echo.
echo [8/11] TYPE 7 — API Tests
python -m pytest test_7_api.py -v -s --tb=short 2>&1 | tee results\api.txt

echo.
echo [9/11] TYPE 8 — Network Mocking Tests
python -m pytest test_8_network_mocking.py -v -s --tb=short 2>&1 | tee results\network.txt

echo.
echo [10/11] TYPE 9 — Accessibility Tests
python -m pytest test_9_accessibility.py -v -s --tb=short 2>&1 | tee results\accessibility.txt

echo.
echo [11/11] TYPE 10 — Cross-Browser Tests (Chromium)
python -m pytest test_10_crossbrowser_and_bugs.py -v --tb=short -k "not bug" 2>&1 | tee results\crossbrowser_chromium.txt

echo.
echo ---- INTENTIONAL BUG DEMO (expected failures) ----
python -m pytest test_10_crossbrowser_and_bugs.py -v --tb=short -k "bug" 2>&1 | tee results\bug_demo.txt

echo.
echo ---- FIREFOX CROSS-BROWSER ----
python -m pytest test_10_crossbrowser_and_bugs.py -v --browser firefox --tb=short -k "not bug" 2>&1 | tee results\crossbrowser_firefox.txt

echo.
echo ---- FULL HTML REPORT ----
python -m pytest --html=test_report.html --self-contained-html -v --tb=short --screenshot only-on-failure

echo.
echo ================================================
echo  DONE! Open test_report.html in your browser.
echo ================================================
pause

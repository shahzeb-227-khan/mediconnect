@echo off
title MediConnect CEP Tests - Running...
cd /d "%~dp0"

echo ================================================
echo  MediConnect Playwright Test Suite - CEP
echo ================================================
echo.

REM Login tests need a real account. Set these once in this window before running:
REM   set MEDI_TEST_EMAIL=your_test_account@example.com
REM   set MEDI_TEST_PASSWORD=your_test_password
if "%MEDI_TEST_EMAIL%"=="" echo WARNING: MEDI_TEST_EMAIL is not set. Login tests will fail.
if "%MEDI_TEST_PASSWORD%"=="" echo WARNING: MEDI_TEST_PASSWORD is not set. Login tests will fail.
echo.

echo [Step 1] Installing test dependencies...
pip install pytest-playwright pytest-html --quiet 2>nul
playwright install chromium --quiet 2>nul
playwright install firefox --quiet 2>nul

echo [Step 2] Creating results folder...
if not exist results mkdir results

echo.
echo [Step 3] Running ALL tests on Chromium with HTML report...
python -m pytest test_01_functional.py test_02_navigation.py test_03_api.py test_04_network_mocking.py test_05_crossbrowser_bugs.py -v --tb=short --html=test_report.html --self-contained-html 2>&1 | tee results\all_tests.txt

echo.
echo [Step 4] Running Firefox cross-browser tests...
python -m pytest test_05_crossbrowser_bugs.py -v --browser firefox --tb=short -k "not bug" 2>&1 | tee results\firefox.txt

echo.
echo [Step 5] Running BUG DEMO (intentional failures, expected to FAIL)...
python -m pytest test_05_crossbrowser_bugs.py -v --tb=short -k "bug" 2>&1 | tee results\bug_demo.txt

echo.
echo ================================================
echo  DONE! Results saved to results\ folder
echo  Open test_report.html in your browser
echo ================================================
pause

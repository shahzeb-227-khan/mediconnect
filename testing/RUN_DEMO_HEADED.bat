@echo off
title MediConnect CEP - DEMO MODE (Browser Visible)
cd /d "%~dp0"

echo ================================================
echo  MediConnect Playwright - DEMO MODE
echo  Browser will open and you can watch tests run!
echo ================================================
echo.

REM Set these once in this window before running (see RUN_TESTS_NOW.bat):
REM   set MEDI_TEST_EMAIL=your_test_account@example.com
REM   set MEDI_TEST_PASSWORD=your_test_password

echo [1/4] Feature 1 - Patient Login Demo
python -m pytest test_01_functional.py::TestPatientLoginFunctional -v --headed --slowmo 800 --tb=short

echo.
echo [2/4] Feature 2 - Patient Signup Demo
python -m pytest test_01_functional.py::TestSignupFunctional -v --headed --slowmo 800 --tb=short

echo.
echo [3/4] Feature 3 - Hospital Search Demo
python -m pytest test_01_functional.py::TestHospitalSearchFunctional -v --headed --slowmo 800 --tb=short

echo.
echo [4/4] Feature 4 - Navigation Demo
python -m pytest test_02_navigation.py -v --headed --slowmo 800 --tb=short

echo.
echo ---- API Tests (no browser needed) ----
python -m pytest test_03_api.py -v -s --tb=short

echo.
echo ---- Network Mocking Demo ----
python -m pytest test_04_network_mocking.py -v --headed --slowmo 1000 --tb=short

echo.
echo ---- BUG DEMO (intentional failures) ----
python -m pytest test_05_crossbrowser_bugs.py -v --headed --slowmo 800 -k "bug" --tb=short

echo.
echo ================================================
echo  DEMO COMPLETE!
echo ================================================
pause

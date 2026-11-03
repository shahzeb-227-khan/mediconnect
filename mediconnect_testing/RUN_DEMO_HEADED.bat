@echo off
title MediConnect CEP - DEMO MODE (Browser Visible)
cd /d "%~dp0"

echo ================================================
echo  MediConnect Playwright - DEMO MODE
echo  Browser will open and you can watch tests run!
echo ================================================
echo.

REM Set these once in this window before running:
REM   set MEDI_TEST_EMAIL=your_test_account@example.com
REM   set MEDI_TEST_PASSWORD=your_test_password

echo [1/5] Feature 1 - Patient Login Demo
python -m pytest test_01_functional.py::TestFeature1_PatientLogin -v --headed --slowmo 800 --tb=short

echo.
echo [2/5] Feature 2 - Patient Signup Demo
python -m pytest test_01_functional.py::TestFeature2_PatientSignup -v --headed --slowmo 800 --tb=short

echo.
echo [3/5] Feature 3 - Hospital Search Demo
python -m pytest test_01_functional.py::TestFeature3_HospitalSearch -v --headed --slowmo 800 --tb=short

echo.
echo [4/5] Feature 4 - Doctor Login Demo
python -m pytest test_01_functional.py::TestFeature4_DoctorLogin -v --headed --slowmo 800 --tb=short

echo.
echo [5/5] Network Mocking Demo
python -m pytest test_04_network_mocking.py -v --headed --slowmo 1000 --tb=short

echo.
echo ---- API Tests (no browser needed) ----
python -m pytest test_03_api.py -v -s --tb=short

echo.
echo ================================================
echo  DEMO COMPLETE!
echo ================================================
pause

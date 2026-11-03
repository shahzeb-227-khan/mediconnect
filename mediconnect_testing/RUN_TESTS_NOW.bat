@echo off
title MediConnect CEP - Complete Test Suite
cd /d "%~dp0"

echo ================================================================
echo   MediConnect Playwright Test Suite - CEP Submission
echo   Muhammad Shahzeb Alam (SE-23055) ^& Muneeb Asghar (SE-23082)
echo ================================================================
echo.

REM ── Check credentials ──────────────────────────────────────────
if "%MEDI_TEST_EMAIL%"=="" (
    echo [!] WARNING: MEDI_TEST_EMAIL is not set. Login tests will fail.
    echo     Run:  set MEDI_TEST_EMAIL=your_email@example.com
)
if "%MEDI_TEST_PASSWORD%"=="" (
    echo [!] WARNING: MEDI_TEST_PASSWORD is not set. Login tests will fail.
    echo     Run:  set MEDI_TEST_PASSWORD=your_password
)
echo.

REM ── Install dependencies ───────────────────────────────────────
echo [Step 1/8] Installing dependencies...
pip install pytest-playwright pytest-html --quiet 2>nul
playwright install chromium --quiet 2>nul
playwright install firefox --quiet 2>nul
playwright install webkit --quiet 2>nul

if not exist results mkdir results
if not exist screenshots mkdir screenshots
echo.

REM ── Path to Login.jsx (the file we will temporarily modify) ────
set LOGIN_FILE=..\frontend\src\pages\patient\Login.jsx

REM ── STEP 2: Run ALL tests on Chromium ──────────────────────────
echo [Step 2/8] Running ALL tests on CHROMIUM...
python -m pytest test_01_functional.py test_02_navigation.py test_03_api.py test_04_network_mocking.py test_05_crossbrowser_bugs.py -v --tb=short --html=test_report.html --self-contained-html -k "not bug" 2>&1 | tee results\chromium_all.txt
echo.

REM ── STEP 3: Run cross-browser tests on FIREFOX ────────────────
echo [Step 3/8] Running cross-browser tests on FIREFOX...
python -m pytest test_05_crossbrowser_bugs.py -v --browser firefox --tb=short -k "not bug" 2>&1 | tee results\firefox_crossbrowser.txt
echo.

REM ── STEP 4: Run cross-browser tests on WEBKIT ─────────────────
echo [Step 4/8] Running cross-browser tests on WEBKIT...
python -m pytest test_05_crossbrowser_bugs.py -v --browser webkit --tb=short -k "not bug" 2>&1 | tee results\webkit_crossbrowser.txt
echo.

REM ── STEP 5: INSERT INTENTIONAL BUG ────────────────────────────
echo [Step 5/8] INSERTING INTENTIONAL BUG into Login.jsx...
echo            (Changing error message to "BUGGED_ERROR_MSG_12345")

REM Make a backup first
copy /Y "%LOGIN_FILE%" "%LOGIN_FILE%.backup" >nul 2>nul

REM Use PowerShell to do the replacement safely
powershell -Command "(Get-Content '%LOGIN_FILE%') -replace 'setError\(extractErrorMessage\(err\)\)', 'setError(\"BUGGED_ERROR_MSG_12345\")' | Set-Content '%LOGIN_FILE%'"

echo            Bug inserted! Waiting 5 seconds for Vite hot-reload...
timeout /t 5 /nobreak >nul
echo.

REM ── STEP 6: Run bug test (SHOULD FAIL) ─────────────────────────
echo [Step 6/8] Running bug detection test (EXPECTED TO FAIL)...
python -m pytest test_05_crossbrowser_bugs.py::TestIntentionalBug -v --tb=short --screenshot on 2>&1 | tee results\bug_test_FAIL.txt
echo.

REM ── STEP 7: REVERT THE BUG ────────────────────────────────────
echo [Step 7/8] REVERTING BUG (restoring original Login.jsx)...
copy /Y "%LOGIN_FILE%.backup" "%LOGIN_FILE%" >nul 2>nul
del "%LOGIN_FILE%.backup" >nul 2>nul
echo            Bug reverted! Waiting 5 seconds for Vite hot-reload...
timeout /t 5 /nobreak >nul
echo.

REM ── STEP 8: Run bug test again (SHOULD PASS) ──────────────────
echo [Step 8/8] Running bug detection test again (SHOULD PASS NOW)...
python -m pytest test_05_crossbrowser_bugs.py::TestIntentionalBug -v --tb=short 2>&1 | tee results\bug_test_PASS.txt
echo.

REM ── Take screenshots of test_report.html ───────────────────────
echo Copying test report to results folder...
copy /Y test_report.html results\ >nul 2>nul

echo.
echo ================================================================
echo   ALL DONE!
echo.
echo   Results in:  results\
echo     chromium_all.txt       - All tests on Chromium
echo     firefox_crossbrowser.txt - Cross-browser on Firefox
echo     webkit_crossbrowser.txt  - Cross-browser on WebKit
echo     bug_test_FAIL.txt      - Bug test failing (bug present)
echo     bug_test_PASS.txt      - Bug test passing (bug fixed)
echo     test_report.html       - HTML report
echo.
echo   Screenshots: screenshots\ (failure screenshots auto-saved)
echo.
echo   NEXT: Copy results\ and screenshots\ contents,
echo         then send them to Claude for final report + ZIP.
echo ================================================================
pause

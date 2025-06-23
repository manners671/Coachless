@echo off
REM ── run_coachlessai.bat ──

REM Change directory to the folder this batch file lives in:
cd /d "%~dp0"

REM (Re-)install dependencies on this machine if you haven’t yet:
pip install --upgrade pip
pip install -r requirements.txt

REM Launch the Streamlit app
streamlit run app.py

pause

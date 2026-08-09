@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE="
for %%I in (py.exe python.exe) do (
  where %%I >nul 2>nul
  if not errorlevel 1 set "PYTHON_EXE=%%I"
)

if not defined PYTHON_EXE (
  echo Could not find Python on PATH.
  echo Install Python and try again, or run the API with a Python interpreter directly.
  exit /b 1
)

echo Starting Curriculum Recommender API at http://127.0.0.1:8000
if /I "%PYTHON_EXE%"=="py.exe" (
  py -3 -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
) else (
  "%PYTHON_EXE%" -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
)

@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
REM Windows launcher: run GUI from WSL UNC path using pushd mapping

set "DISTRO=Ubuntu-24.04"
set "USERNAME=rays"

REM If current dir looks like the project, use it; else use UNC path
if exist "bluev\main.py" (
  set "PROJ=%CD%"
) else (
  set "PROJ=\\wsl.localhost\%DISTRO%\home\%USERNAME%\dev\OneDay_BuleV"
)

echo [BlueV] Project: %PROJ%
pushd "%PROJ%" || (echo [BlueV] ERROR: Cannot access %PROJ% & exit /b 1)

REM Use a local Windows venv to avoid pip issues on network shares
set "VENV_DIR=%LOCALAPPDATA%\BlueV\.win-venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

if not exist "%VENV_PY%" (
  echo [BlueV] Creating venv in %VENV_DIR%
  py -3 -m venv "%VENV_DIR%"
)
call "%VENV_DIR%\Scripts\activate"

REM Ensure pip is available in this venv
"%VENV_PY%" -m ensurepip --upgrade

REM Upgrade pip toolchain
"%VENV_PY%" -m pip install --upgrade pip setuptools wheel

if exist requirements.txt (
  echo [BlueV] Installing requirements.txt
  "%VENV_PY%" -m pip install -r requirements.txt
)
if exist requirements-dev.txt (
  echo [BlueV] Installing requirements-dev.txt
  "%VENV_PY%" -m pip install -r requirements-dev.txt
)

REM Fallback: ensure python-dotenv is present if project needs it
"%VENV_PY%" -c "import importlib, sys; sys.exit(0 if importlib.util.find_spec('dotenv') else 1)" || (
  echo [BlueV] Installing missing dependency: python-dotenv
  "%VENV_PY%" -m pip install python-dotenv
)

echo [BlueV] Starting GUI...
"%VENV_PY%" -m bluev.main

popd
endlocal

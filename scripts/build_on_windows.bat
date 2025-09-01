@echo off
setlocal
chcp 65001 >nul
REM Windows build script: package from WSL UNC via pushd mapping

set "DISTRO=Ubuntu-24.04"
set "USERNAME=rays"

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

echo [BlueV] Installing PyInstaller
"%VENV_PY%" -m pip install pyinstaller

set "ICON_PATH=resources\icons\app_icon.ico"
set "ICON_ARG="
if exist "%ICON_PATH%" (
  set "ICON_ARG=--icon %ICON_PATH%"
)

REM Build (onedir) — avoid line continuations for safer parsing
"%VENV_PY%" -m PyInstaller --name BlueV --windowed %ICON_ARG% --add-data "resources;resources" --exclude-module tkinter --exclude-module matplotlib bluev\main.py

if exist dist\BlueV\BlueV.exe (
  echo.
  echo [BlueV] 打包成功：dist\BlueV\BlueV.exe
) else (
  echo.
  echo [BlueV] 打包失败，请检查上方日志
  exit /b 1
)

popd
endlocal

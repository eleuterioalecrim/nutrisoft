@echo off
title Instalador NutriSoft
cd /d "%~dp0"

echo ============================================================
echo Instalando NutriSoft
echo ============================================================

python --version
IF ERRORLEVEL 1 (
    echo Python nao encontrado. Instale Python 3.10 ou superior.
    pause
    exit /b 1
)

python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Instalacao concluida.
echo Para iniciar, execute: INICIAR_NUTRISOFT_WINDOWS.bat
pause

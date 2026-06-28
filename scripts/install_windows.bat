@echo off
cd /d "%~dp0.."
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Instalacao concluida.
echo Execute: iniciar_nutrisoft_windows.bat
pause

#!/usr/bin/env bash
cd "$(dirname "$0")/.."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Instalação concluída."
echo "Execute: ./iniciar_nutrisoft_linux.sh"

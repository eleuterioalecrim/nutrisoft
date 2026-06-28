#!/usr/bin/env bash
cd "$(dirname "$0")"

echo "============================================================"
echo "Instalando NutriSoft"
echo "============================================================"

if ! command -v python3 &> /dev/null
then
    echo "Python3 não encontrado. Instale Python 3.10 ou superior."
    exit 1
fi

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Instalação concluída."
echo "Para iniciar, execute: ./INICIAR_NUTRISOFT_LINUX.sh"

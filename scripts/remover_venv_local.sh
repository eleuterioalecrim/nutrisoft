#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

if [ -d ".venv" ]; then
    echo "Removendo ambiente virtual local .venv..."
    rm -rf .venv
    echo ".venv removido."
else
    echo "Nenhum .venv encontrado."
fi

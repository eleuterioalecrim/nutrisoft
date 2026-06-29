#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

echo "============================================================"
echo "NutriSoft - Instalação Linux sem ambiente virtual"
echo "============================================================"
echo ""

PYTHON_CMD="${PYTHON_CMD:-python3}"

if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
    echo "ERRO: python3 não encontrado."
    echo "Instale com:"
    echo "sudo apt update && sudo apt install python3 python3-pip -y"
    exit 1
fi

echo "Python encontrado:"
"$PYTHON_CMD" --version
echo ""

echo "Verificando pip..."
if ! "$PYTHON_CMD" -m pip --version >/dev/null 2>&1; then
    echo "pip não encontrado. Tentando instalar python3-pip..."
    sudo apt update
    sudo apt install python3-pip -y
fi

echo ""
echo "Atualizando pip no perfil do usuário..."
"$PYTHON_CMD" -m pip install --user --upgrade pip || true

echo ""
echo "Instalando bibliotecas no perfil do usuário..."
if "$PYTHON_CMD" -m pip install --user -r requirements.txt; then
    echo "Bibliotecas instaladas com sucesso."
else
    echo ""
    echo "A instalação padrão foi bloqueada pelo gerenciamento externo do Python."
    echo "Tentando novamente com --break-system-packages no perfil do usuário..."
    "$PYTHON_CMD" -m pip install --user --break-system-packages -r requirements.txt
fi

echo ""
echo "Verificando ambiente..."
"$PYTHON_CMD" scripts/verificar_ambiente.py

echo ""
echo "Instalação concluída."
echo "Para iniciar:"
echo "./INICIAR_NUTRISOFT_LINUX_SEM_VENV.sh"

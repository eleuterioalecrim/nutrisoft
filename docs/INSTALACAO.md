# Instalação do NutriSoft

## Requisitos

- Python 3.10 ou superior.
- Git instalado, caso vá clonar o repositório.
- Navegador web.

## Instalação via GitHub

```bash
git clone https://github.com/eleuterioalecrim/nutrisoft.git
cd nutrisoft
```

## Linux

```bash
chmod +x scripts/install_linux.sh
./scripts/install_linux.sh
./iniciar_nutrisoft_linux.sh
```

## Windows

Execute:

```bat
scripts\install_windows.bat
iniciar_nutrisoft_windows.bat
```

## Execução manual

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bat
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute:

```bash
streamlit run app_web.py
```

## Endereço local

Normalmente a aplicação abre em:

```text
http://localhost:8501
```

# NutriSoft - Instalação Completa no Windows

Este modo de instalação foi criado para ambientes Microsoft/Windows onde o usuário
pode não ter Python instalado.

## Arquivo principal

Execute:

```bat
INSTALAR_COMPLETO_NUTRISOFT_WINDOWS.bat
```

Ele tentará:

1. Verificar se o Python já existe.
2. Instalar Python 3.12 via WinGet, se necessário.
3. Criar o ambiente virtual `.venv`.
4. Instalar as bibliotecas do `requirements.txt`.
5. Validar o ambiente.
6. Preparar o sistema para execução.

## Abrir o sistema

Após a instalação, execute:

```bat
INICIAR_NUTRISOFT_WINDOWS.bat
```

O sistema abrirá no navegador:

```text
http://localhost:8501
```

## Quando usar o instalador ADMIN

Caso o Windows bloqueie a instalação do Python, use:

```bat
INSTALAR_COMPLETO_NUTRISOFT_WINDOWS_ADMIN.bat
```

## Instalação offline

Caso a máquina não tenha internet ou não tenha WinGet:

1. Baixe em outra máquina o instalador oficial do Python para Windows.
2. Use a versão 64 bits, por exemplo:

```text
python-3.12.x-amd64.exe
```

3. Coloque o arquivo na pasta:

```text
installers/
```

4. Execute:

```bat
INSTALAR_COMPLETO_NUTRISOFT_WINDOWS.bat
```

## Observações

- O Python será instalado no perfil do usuário, quando possível.
- O ambiente virtual fica dentro da pasta `.venv`.
- As bibliotecas são instaladas apenas no ambiente do NutriSoft.
- Não é recomendado publicar dados reais de pacientes no GitHub.

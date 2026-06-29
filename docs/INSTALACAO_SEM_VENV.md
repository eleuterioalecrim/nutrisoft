# NutriSoft - Instalação sem ambiente virtual

Esta opção roda o NutriSoft diretamente com o Python do sistema/usuário,
sem criar a pasta `.venv`.

## Linux

Instalar dependências:

```bash
./scripts/install_linux_sem_venv.sh
```

Iniciar:

```bash
./INICIAR_NUTRISOFT_LINUX_SEM_VENV.sh
```

Ou:

```bash
./INICIAR_NUTRISOFT_LINUX.sh
```

## Remover `.venv` antigo

Caso exista um ambiente virtual antigo:

```bash
./scripts/remover_venv_local.sh
```

## Observação

Em algumas distribuições Linux, o Python bloqueia instalações globais via `pip`
por proteção do sistema. Por isso este instalador usa `pip install --user`.

Se ainda houver bloqueio, o script tenta `--break-system-packages` apenas no contexto do usuário.
Isso evita a necessidade de ativar ambiente virtual.

## Windows

Instalar dependências:

```bat
python -m pip install --user -r requirements.txt
```

Iniciar:

```bat
INICIAR_NUTRISOFT_WINDOWS_SEM_VENV.bat
```

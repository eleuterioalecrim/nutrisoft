# NutriSoft - Pacote Instalável

Este documento explica como instalar e executar o NutriSoft em Windows e Linux.

## Windows

1. Extraia o arquivo `.zip` do NutriSoft.
2. Abra a pasta extraída.
3. Execute:

```bat
INSTALAR_NUTRISOFT_WINDOWS.bat
```

4. Depois da instalação, execute:

```bat
INICIAR_NUTRISOFT_WINDOWS.bat
```

## Linux

1. Extraia o arquivo `.zip` do NutriSoft.
2. Abra o terminal dentro da pasta.
3. Dê permissão de execução:

```bash
chmod +x INSTALAR_NUTRISOFT_LINUX.sh
chmod +x INICIAR_NUTRISOFT_LINUX.sh
```

4. Instale:

```bash
./INSTALAR_NUTRISOFT_LINUX.sh
```

5. Execute:

```bash
./INICIAR_NUTRISOFT_LINUX.sh
```

## Endereço da aplicação

A aplicação abrirá no navegador, normalmente em:

```text
http://localhost:8501
```

## Verificar ambiente

Windows:

```bat
scripts\verificar_ambiente.bat
```

Linux:

```bash
scripts/verificar_ambiente.sh
```

## Dados de exemplo

Para carregar dados fictícios de teste:

Windows:

```bat
scripts\carregar_dados_exemplo.bat
```

Linux:

```bash
scripts/carregar_dados_exemplo.sh
```

## Observação

Não publique dados reais de pacientes em repositórios públicos ou em pacotes compartilhados.

# NutriSoft

Aplicação local e multiplataforma para cadastro, anamnese, avaliação antropométrica,
registro de exames, análise comparativa de resultados laboratoriais e dashboards nutricionais.

## Versão atual

**v1.0 - Passo 10**

Esta versão prepara o NutriSoft como pacote instalável/simplificado para Windows e Linux.

## Interface principal

O NutriSoft roda como uma aplicação web local com Streamlit:

```bash
streamlit run app_web.py
```

Endereço padrão:

```text
http://localhost:8501
```

## Instalação simplificada

### Windows

Execute:

```bat
INSTALAR_NUTRISOFT_WINDOWS.bat
```

Depois:

```bat
INICIAR_NUTRISOFT_WINDOWS.bat
```

### Linux

Execute:

```bash
chmod +x INSTALAR_NUTRISOFT_LINUX.sh
chmod +x INICIAR_NUTRISOFT_LINUX.sh
./INSTALAR_NUTRISOFT_LINUX.sh
./INICIAR_NUTRISOFT_LINUX.sh
```

## Verificação de ambiente

```bash
python scripts/verificar_ambiente.py
```

## Dados de exemplo

```bash
python scripts/carregar_dados_exemplo.py
```

## Documentação

```text
docs/INSTALACAO.md
docs/USO.md
docs/GITHUB.md
docs/PACOTE_INSTALAVEL.md
docs/USUARIO_FINAL.md
ARQUITETURA.md
CHANGELOG.md
```

## Estrutura principal

```text
nutrisoft/
├── app.py
├── app_web.py
├── INSTALAR_NUTRISOFT_WINDOWS.bat
├── INICIAR_NUTRISOFT_WINDOWS.bat
├── INSTALAR_NUTRISOFT_LINUX.sh
├── INICIAR_NUTRISOFT_LINUX.sh
├── requirements.txt
├── data/
├── data_examples/
├── docs/
├── src/
├── reports/
└── scripts/
```

## Atenção sobre dados reais

Não publique dados reais de pacientes em repositórios públicos.

## Observação importante

O NutriSoft é uma ferramenta de apoio à análise profissional.
Ele não substitui diagnóstico, prescrição ou conduta clínica individualizada.

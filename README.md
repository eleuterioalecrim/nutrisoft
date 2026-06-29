# NutriSoft

Aplicação local e multiplataforma para cadastro, anamnese, avaliação antropométrica,
registro de exames, análise comparativa de resultados laboratoriais e dashboards nutricionais.

## Versão atual

**v1.13 - Exclusão dentro da sessão Pacientes**

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

## Instalação completa no Windows

Para ambiente Microsoft/Windows sem Python instalado, use:

```bat
INSTALAR_COMPLETO_NUTRISOFT_WINDOWS.bat
```

Depois execute:

```bat
INICIAR_NUTRISOFT_WINDOWS.bat
```

Caso precise executar com permissão elevada:

```bat
INSTALAR_COMPLETO_NUTRISOFT_WINDOWS_ADMIN.bat
```

Documentação detalhada:

```text
docs/INSTALACAO_WINDOWS_COMPLETA.md
```


## v1.2 - Anamnese guiada e dashboard clínico

Melhorias principais:

- Redução de campos de escrita livre na anamnese.
- Uso de listas suspensas e múltipla seleção.
- Opções padronizadas baseadas na ficha de anamnese.
- Cadastro de exames com lista de exames comuns.
- Cadastro de unidades com lista suspensa.
- Análise de exames por painéis.
- Dashboard com resumo executivo, prioridades e alertas.
- Recomendações de fluxo sem diagnóstico automático.

Documento:

```text
docs/MELHORIAS_V1_2.md
```

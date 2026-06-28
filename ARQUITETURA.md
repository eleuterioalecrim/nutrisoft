# Arquitetura do NutriSoft

## Decisão arquitetural

A interface principal do NutriSoft é uma **interface web local com Streamlit**.

Esta decisão substitui a ideia inicial de uma interface desktop tradicional com Tkinter,
mantendo coerência com o modelo utilizado no projeto de Análise Comparativa de Dados.

## Stack principal

```text
Python
+ CSV como banco local
+ Pandas para manipulação de dados
+ Matplotlib para gráficos exportáveis
+ Streamlit para interface web local
```

## Entradas da aplicação

```text
app_web.py  -> interface principal com Streamlit
app.py      -> modo terminal/técnico/fallback
```

## Separação de responsabilidades

```text
src/
├── pacientes.py        -> regra de negócio de pacientes
├── anamnese.py         -> regra de negócio de anamnese
├── antropometria.py    -> regra de negócio de antropometria
├── exames.py           -> regra de negócio de exames
├── analises.py         -> motor comparativo
├── dashboard.py        -> consolidação de indicadores
├── graficos.py         -> geração de gráficos
└── web/                -> componentes visuais Streamlit
```

## Estrutura web

```text
src/web/
├── common.py
├── styles.py
├── page_inicio.py
├── page_pacientes.py
├── page_anamnese.py
├── page_antropometria.py
├── page_exames.py
├── page_dashboard.py
└── page_bases.py
```

## Princípios

1. O sistema deve funcionar em Linux e Windows.
2. O banco local deve continuar em CSV.
3. A lógica de negócio deve ficar em `src/`.
4. A interface principal deve ficar em `app_web.py` e `src/web/`.
5. O modo terminal deve ser preservado como ferramenta técnica.
6. O sistema não deve realizar diagnóstico automático.
7. A análise deve apontar valores fora da referência cadastrada e apoiar o profissional.

# NutriSoft v1.6 - Layout moderno e indicador de completude

## Melhorias de layout

- Visual mais clean e profissional.
- Sidebar reorganizada por grupos:
  - Operação;
  - Análise;
  - Gestão.
- Cabeçalho mais moderno.
- Cards, métricas e abas com estilo visual mais leve.
- Página inicial com visão executiva.

## Indicador de completude

Criado o módulo:

```text
src/completude.py
```

O cálculo considera:

- cadastro básico;
- anamnese;
- recordatório;
- antropometria;
- exames;
- análise comparativa.

## Nova página

```text
Menu lateral → Completude
```

A página mostra:

- ranking de completude dos pacientes;
- média geral;
- pacientes abaixo do aceitável;
- detalhe por paciente;
- pendências objetivas.

## Uso

O indicador ajuda o usuário a identificar rapidamente se o cadastro possui
informações suficientes para análise e acompanhamento.

# NutriSoft v1.12 - Menu lateral com UX atual

## Problema corrigido

O menu v1.11 usava cards com botões invisíveis, o que deixava a experiência ruim.

## Solução

A navegação foi refeita com links reais em HTML/CSS usando query string:

```text
?page=Dashboard
```

## Melhorias

- Remoção da lista suspensa.
- Remoção dos botões invisíveis.
- Menu com links reais.
- Hover visual quando o mouse passa por cima.
- Página ativa com:
  - borda destacada;
  - sombra;
  - barra lateral verde;
  - ponto indicador;
  - ícone destacado.
- Próxima etapa do fluxo também clicável.

## Arquivos alterados

```text
src/web/navigation.py
src/web/styles.py
```

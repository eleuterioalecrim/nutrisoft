# Publicação no GitHub

## Repositório

Repositório sugerido:

```text
https://github.com/eleuterioalecrim/nutrisoft.git
```

## Primeiro envio

Dentro da pasta do projeto:

```bash
git init
git branch -M main
git remote add origin https://github.com/eleuterioalecrim/nutrisoft.git
git add .
git commit -m "Versão inicial do NutriSoft"
git push -u origin main
```

## Atualizações futuras

```bash
git add .
git commit -m "Descreva a melhoria realizada"
git push
```

## Recomendações

- Não versionar ambiente virtual `.venv/`.
- Não versionar arquivos sensíveis.
- Manter `data_examples/` para demonstração.
- Avaliar se `data/` deve conter dados reais ou apenas bases vazias.
- Não incluir dados pessoais reais de pacientes no GitHub.

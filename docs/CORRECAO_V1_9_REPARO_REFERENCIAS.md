# NutriSoft v1.9 - Reparo forçado de referências e análises

## Problema corrigido

Em versões anteriores, exames poderiam aparecer como `Sem referência` quando:

- a máquina ainda estava em versão antiga;
- as referências padrão não tinham sido carregadas no CSV preservado;
- os aliases ainda não tinham sido gravados;
- a análise estava desatualizada depois de atualizar o catálogo.

## Correção

A v1.9 adiciona:

- carga idempotente de referências e aliases;
- fallback de aliases direto do catálogo;
- reprocessamento automático das análises na abertura;
- botão de reparo manual;
- script de reparo via terminal.

## Botão na interface

Caminho:

```text
Exames → Análise orientada → Reparar referências e reprocessar análises
```

## Script no terminal

```bash
python scripts/reparar_referencias_e_analises.py
```

## Resultado esperado

Para exames existentes no catálogo, o status `Sem referência` deve desaparecer após o reparo.

Se ainda restarem exames sem referência, provavelmente eles foram cadastrados manualmente como `Outro`
com nome diferente do catálogo ou unidade muito específica. Nesse caso, o script lista esses nomes.

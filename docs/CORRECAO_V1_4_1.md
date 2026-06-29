# NutriSoft v1.4.1 - Correção de PDF, gráficos e menu Edição

## Correções

### 1. Erro `StreamlitDuplicateElementKey`

O botão de PDF aparecia em mais de um local com a mesma chave.
Agora cada botão recebe uma chave diferente conforme o contexto:

- `painel`;
- `aba_pdf`.

### 2. Gráficos na tela

Foram adicionados tratamentos para dados vazios e mensagens orientando o fluxo:

1. cadastrar exames;
2. carregar referências padrão;
3. executar análise comparativa;
4. abrir Dashboard.

### 3. View de Edição

O arquivo `app_web.py` foi reconstruído explicitamente incluindo:

```text
Edição
```

no menu lateral.

## Como acessar

```text
Menu lateral → Edição
```

# NutriSoft v1.4 - Dashboard com gráficos em tela e PDF visível

## Ajustes realizados

### 1. Botão de PDF mais visível

O Dashboard agora possui uma aba específica:

```text
Relatório PDF
```

Além disso, o botão também aparece dentro de:

```text
Painel do paciente → Relatório
```

Botão:

```text
📄 Gerar PDF da análise do paciente
```

### 2. Gráficos diretamente na tela

A aba antiga de geração de PNG foi removida do fluxo principal.

Agora os gráficos aparecem diretamente no Streamlit:

- distribuição dos exames por status;
- exames mais alterados;
- distribuição dos exames do paciente;
- prioridade por painel;
- evolução antropométrica.

### 3. PNG deixa de ser fluxo principal

A geração de arquivos PNG não é mais necessária para visualizar os gráficos.
A visualização passa a ser direta na tela do Dashboard.

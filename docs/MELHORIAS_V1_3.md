# NutriSoft v1.3 - Referências, Edição, Exportação e PDF

## Melhorias

### 1. Catálogo inicial de exames

Foi criado um catálogo com exames comuns, aliases, unidades e referências iniciais.

Arquivos:

```text
src/catalogo_exames.py
src/referencias_padrao.py
```

Na tela de Exames, em Referências, use:

```text
Carregar referências e aliases padrão
```

As referências são modelo inicial editável e devem ser revisadas conforme laboratório,
método, faixa etária, sexo e protocolo profissional.

### 2. Mais esportes na anamnese

A lista de atividade física foi ampliada para incluir esportes como:

- Karatê;
- Kempo;
- Judô;
- Jiu-jitsu;
- Triathlon;
- Ciclismo;
- Corrida;
- Futebol;
- Beach tennis;
- Musculação;
- Cross training;
- Dança;
- Surf;
- Trilha;
- entre outros.

### 3. CSV com nome do paciente

A tela Bases CSV agora exporta os arquivos enriquecidos com:

```text
paciente_nome
```

quando a base possui `paciente_id`.

### 4. Edição com histórico

Foi criada uma nova tela:

```text
Edição
```

Cada alteração grava histórico em:

```text
data/historico_edicoes.csv
```

### 5. PDF para impressão

O Dashboard do paciente agora permite gerar PDF da análise do paciente.

O arquivo é salvo em:

```text
reports/pdf/
```

O PDF inclui:

- dados do paciente;
- resumo executivo dos exames;
- recomendações de fluxo;
- antropometria atual;
- anamnese recente;
- recordatório recente;
- prioridades por painel;
- exames analisados;
- observação de apoio profissional.

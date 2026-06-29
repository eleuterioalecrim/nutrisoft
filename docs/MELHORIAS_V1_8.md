# NutriSoft v1.8 - Lista suspensa inteligente e referências rastreáveis

## 1. Lista suspensa de exames

O cadastro de exames foi corrigido para que a data do exame fique fora do formulário e seja a referência da lista suspensa.

Resultado:

- escolheu a data;
- o sistema consulta exames do paciente naquela data;
- exames já cadastrados deixam de aparecer na lista;
- a comparação usa nome canônico/alias, não apenas texto exato;
- a tentativa de duplicidade manual continua bloqueada.

Exemplos de equivalência:

- Glicose;
- Glicemia;
- Glicemia de jejum.

Se um deles já foi cadastrado para a data, o grupo deixa de aparecer como opção equivalente.

## 2. Referências carregadas automaticamente

As referências e aliases padrão agora são carregados automaticamente na inicialização do sistema.

A rotina é idempotente:

- cria o que falta;
- ignora o que já existe;
- não duplica referências já cadastradas.

## 3. Cobertura do catálogo

A tela de Referências agora mostra:

- total de tipos de exames;
- total de referências cadastráveis;
- percentual de cobertura;
- alerta caso exista algum exame sem referência.

## 4. Fontes rastreáveis

As referências agora gravam fonte por grupo de exames, incluindo:

- Merck Manual Professional - Laboratory Reference Ranges;
- MedlinePlus/NLM - CBC;
- MedlinePlus/NLM - Lipid profile;
- MedlinePlus/NLM - Comprehensive metabolic panel;
- MedlinePlus/NLM - TSH/T4;
- UCSF Health - Ferritin;
- Mayo Clinic Laboratories - 25-Hydroxyvitamin D.

Observação: os valores permanecem editáveis porque intervalos laboratoriais variam por método, equipamento, unidade, idade, sexo e contexto clínico.

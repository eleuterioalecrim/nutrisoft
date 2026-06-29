# Changelog


## v1.13 - Exclusão dentro da sessão Pacientes

- Reformulada `src/web/page_pacientes.py`.
- Adicionada aba `Ações` em Pacientes.
- Adicionado botão de exclusão total do paciente.
- Adicionada confirmação via `st.dialog` quando disponível.
- Removida opção separada `Exclusão de paciente` do menu Gestão.
- Atualizado `app_web.py` para remover rota separada.
- Criado `docs/EXCLUSAO_PACIENTE_V1_13.md`.



## v1.12 - Menu lateral com UX atual

- Refeito `src/web/navigation.py` com links reais via query string.
- Removido padrão de botão invisível do menu.
- Atualizado `src/web/styles.py` com hover e estado ativo.
- Página ativa agora possui barra lateral, borda, sombra e indicador.
- Próxima etapa do fluxo agora é link clicável.
- Criado `docs/MELHORIAS_V1_12_MENU_UX_ATUAL.md`.



## v1.11 - Menu lateral profissional

- Removida navegação por `selectbox`.
- Reformulado `src/web/navigation.py` com menu lateral por cards.
- Atualizado `src/web/styles.py` com estilos do novo menu.
- Adicionado destaque da página ativa.
- Adicionado bloco de próxima etapa no menu lateral.
- Criado `docs/MELHORIAS_V1_11_MENU_LATERAL.md`.



## v1.10 - Exclusão segura de paciente

- Criado `src/exclusao_paciente.py`.
- Criado `src/web/page_exclusao_paciente.py`.
- Adicionada opção `Exclusão de paciente` no menu de Gestão.
- Atualizado `app_web.py` para carregar a nova tela.
- Criado `scripts/excluir_paciente.py`.
- Criado `docs/EXCLUSAO_PACIENTE_V1_10.md`.
- Exclusão gera backup automático em `backups/pacientes_excluidos/`.
- Exclusão exige confirmação textual `EXCLUIR <paciente_id>`.



## v1.9.1 - Execução sem ambiente virtual

- Criado `scripts/install_linux_sem_venv.sh`.
- Criado `INICIAR_NUTRISOFT_LINUX_SEM_VENV.sh`.
- Criado `scripts/remover_venv_local.sh`.
- Atualizado `INICIAR_NUTRISOFT_LINUX.sh` para rodar sem `.venv`.
- Criado `INICIAR_NUTRISOFT_WINDOWS_SEM_VENV.bat`.
- Criado `docs/INSTALACAO_SEM_VENV.md`.



## v1.9 - Reparo forçado de referências e análises

- Criado `src/reparo_referencias.py`.
- Criado `scripts/reparar_referencias_e_analises.py`.
- `executar_analise_exames()` agora garante catálogo antes de analisar.
- `carregar_alias()` agora usa aliases do CSV e fallback do catálogo central.
- `app_web.py` executa reparo de referências uma vez por sessão.
- Tela Exames → Análise orientada ganhou botão de reparo manual.
- Sidebar atualizada para v1.9.
- Criado `docs/CORRECAO_V1_9_REPARO_REFERENCIAS.md`.



## v1.8 - Lista suspensa inteligente e referências rastreáveis

- Corrigida a lista suspensa de exames para refletir data selecionada fora do formulário.
- Exames já cadastrados para paciente/data deixam de aparecer no combo.
- Comparação de duplicidade agora usa nome canônico e aliases.
- Catálogo padrão de referências e aliases passa a carregar automaticamente na inicialização.
- Adicionada cobertura do catálogo na tela de referências.
- Fontes de referência foram rastreadas por grupo de exame.
- Criado `docs/MELHORIAS_V1_8.md`.



## v1.7 - Fluxo assistido e bloqueio de exames duplicados

- Criado `src/exames_fluxo.py`.
- Cadastro de exames agora oculta exames já cadastrados na mesma data.
- Validação bloqueia exame duplicado para paciente/data.
- Navegação assistida após salvar paciente, anamnese e antropometria.
- Exames possuem botão manual para concluir sessão e ir ao Dashboard.
- Atualizado `src/web/navigation.py` com controle de fluxo.
- Criado `docs/MELHORIAS_V1_7.md`.



## v1.6 - Layout moderno e indicador de completude

- Criado `src/completude.py`.
- Criado `src/web/navigation.py`.
- Criado `src/web/page_completude.py`.
- Reformulado `app_web.py` para usar navegação centralizada.
- Reformulado `src/web/styles.py` com layout mais moderno.
- Atualizada página inicial com visão executiva.
- Adicionado indicador de completude na página Pacientes.
- Adicionado indicador de completude no Dashboard.
- Criado `docs/MELHORIAS_V1_6.md`.



## v1.5 - Edição guiada e catálogo laboratorial ampliado

- Reformulada `src/web/page_edicao.py` para usar combos/listas na edição.
- Campos de anamnese na edição agora mantêm `selectbox` e `multiselect`.
- Campos de exames e referências na edição agora usam catálogo de exames e unidades.
- Ampliado `src/catalogo_exames.py` com mais painéis laboratoriais.
- Incluídos exames glicêmicos, lipídicos, hemograma, vitaminas, minerais, renal, hepático, tireoidiano, inflamatório e hormonal.
- Criado `docs/MELHORIAS_V1_5.md`.



## v1.4.1 - Correção de PDF, gráficos e menu Edição

- Corrigido erro `StreamlitDuplicateElementKey` no botão de PDF.
- Adicionadas chaves únicas para botões de PDF por contexto.
- Recriado `app_web.py` com a view `Edição` explícita no menu.
- Melhorado tratamento de gráficos sem dados.
- Adicionadas mensagens de pré-requisitos para renderização dos gráficos.
- Criado `docs/CORRECAO_V1_4_1.md`.



## v1.4 - Dashboard com gráficos em tela e PDF visível

- Reformulada a página `src/web/page_dashboard.py`.
- Removida a aba de geração de PNG como fluxo principal.
- Adicionados gráficos diretamente na tela do Streamlit.
- Adicionada aba específica `Relatório PDF`.
- Botão de PDF também exibido no painel do paciente.
- Adicionada evolução antropométrica diretamente em tela.
- Criado `docs/MELHORIAS_V1_4.md`.



## v1.3 - Referências, edição, CSV enriquecido e PDF

- Criado `src/catalogo_exames.py`.
- Criado `src/referencias_padrao.py`.
- Criado botão para carregar referências e aliases padrão.
- Ampliada lista de esportes na anamnese.
- Criado `src/exportacao.py`.
- Bases CSV agora podem ser exportadas com `paciente_nome`.
- Criado `src/edicoes.py`.
- Criada tela `src/web/page_edicao.py`.
- Adicionado `historico_edicoes.csv`.
- Criado `src/relatorio_pdf.py`.
- Adicionada geração de relatório PDF no Dashboard.
- Adicionado `reportlab` ao `requirements.txt`.
- Criado `docs/MELHORIAS_V1_3.md`.



## v1.2 - Anamnese guiada e dashboard clínico

- Criado `src/opcoes_anamnese.py`.
- Criado `src/interpretacao_exames.py`.
- Reformulada página de anamnese para reduzir escrita livre.
- Adicionados campos de múltipla seleção para sintomas, histórico patológico e histórico familiar.
- Adicionados combos para hábitos, sono, intestino, urinário, dentição, mastigação e ingestão hídrica.
- Melhorado cadastro de exames com lista de exames comuns e unidades comuns.
- Melhorada análise de exames por painéis laboratoriais.
- Dashboard reorganizado em visão geral, painel do paciente e gráficos.
- Adicionado resumo executivo dos exames.
- Adicionadas prioridades por painel.
- Adicionados alertas interpretativos sem diagnóstico automático.
- Criado `docs/MELHORIAS_V1_2.md`.


## v1.1 - Pacote Windows Completo

- Criado `INSTALAR_COMPLETO_NUTRISOFT_WINDOWS.bat`.
- Criado `INSTALAR_COMPLETO_NUTRISOFT_WINDOWS_ADMIN.bat`.
- Criado `scripts/windows_instalador_completo.ps1`.
- Atualizado `INICIAR_NUTRISOFT_WINDOWS.bat` para usar `.venv\Scripts\python.exe`.
- Criada pasta `installers/` para instalação offline do Python.
- Criado `docs/INSTALACAO_WINDOWS_COMPLETA.md`.
- Preparado pacote para instalar Python via WinGet quando necessário.


## v1.0 - Passo 10

- Preparado pacote instalável/simplificado para Windows e Linux.
- Criado `INSTALAR_NUTRISOFT_WINDOWS.bat`.
- Criado `INICIAR_NUTRISOFT_WINDOWS.bat`.
- Criado `INSTALAR_NUTRISOFT_LINUX.sh`.
- Criado `INICIAR_NUTRISOFT_LINUX.sh`.
- Criado `scripts/verificar_ambiente.py`.
- Criado `scripts/verificar_ambiente.bat`.
- Criado `scripts/verificar_ambiente.sh`.
- Criado `docs/PACOTE_INSTALAVEL.md`.
- Criado `docs/USUARIO_FINAL.md`.
- Atualizado `README.md`.
- Criado pacote final em `dist/`.

## v0.9 - Passo 9

- Preparado projeto para publicação no GitHub.
- Criada pasta `docs/`.
- Criada pasta `data_examples/`.
- Criados dados de exemplo.
- Criados scripts para carregar dados de exemplo.
- Criado `.env.example`.
- Criado `LICENSE`.
- Criado `CONTRIBUTING.md`.

## v0.8 - Passo 8

- Separada a interface Streamlit em componentes dentro de `src/web/`.
- Melhorado layout visual com CSS customizado.

## v0.7.1 - Passo 7.1

- Removida a pasta `ui/`.
- Confirmado Streamlit como interface principal.
- Criado `ARQUITETURA.md`.

## v0.7 - Passo 7

- Adicionado `app_web.py`.
- Adicionada interface gráfica web local com Streamlit.

## v0.6 - Passo 6

- Adicionado dashboard e gráficos.

## v0.5 - Passo 5

- Adicionado módulo de exames.

## v0.4 - Passo 4

- Adicionado módulo de antropometria.

## v0.3 - Passo 3

- Adicionado módulo de anamnese.

## v0.2 - Passo 2

- Adicionado módulo de pacientes.

## v0.1 - Passo 1

- Criada estrutura inicial do projeto.

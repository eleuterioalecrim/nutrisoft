import pandas as pd
import streamlit as st

from src.anamnese import (
    cadastrar_anamnese,
    cadastrar_recordatorio,
    listar_anamneses_por_paciente,
    listar_recordatorios_por_paciente,
    gerar_resumo_nutricional_paciente,
)
from src.opcoes_anamnese import *
from src.web.common import selecionar_paciente, mostrar_dataframe, csv_multiselect
from src.web.styles import header
from src.web.navigation import avancar_fluxo, mostrar_proxima_etapa


def render():
    header("📝 Anamnese guiada", "Ficha com campos padronizados, listas suspensas e múltipla seleção.")

    st.caption(
        "A ficha foi ajustada para reduzir escrita livre. "
        "Campos abertos ficam reservados para observações relevantes."
    )

    aba_anamnese, aba_recordatorio, aba_historico, aba_resumo = st.tabs([
        "Anamnese guiada",
        "Recordatório guiado",
        "Histórico",
        "Resumo",
    ])

    with aba_anamnese:
        paciente_id = selecionar_paciente("Paciente", key="anamnese_paciente_cadastro")
        if paciente_id:
            with st.form("form_anamnese_guiada", clear_on_submit=True):
                st.subheader("1. Queixa e contexto")
                data_anamnese = st.text_input("Data da anamnese", placeholder="AAAA-MM-DD; vazio = hoje")
                col_q1, col_q2 = st.columns(2)
                with col_q1:
                    queixa_principal = st.selectbox(
                        "Queixa principal",
                        [
                            "",
                            "Emagrecimento",
                            "Ganho de massa muscular",
                            "Reeducação alimentar",
                            "Controle glicêmico",
                            "Controle de colesterol/triglicerídeos",
                            "Melhora intestinal",
                            "Melhora de energia/disposição",
                            "Acompanhamento esportivo",
                            "Acompanhamento gestacional",
                            "Outro",
                        ],
                    )
                with col_q2:
                    comportamento_peso = st.selectbox("Comportamento do peso", COMPORTAMENTO_PESO)

                historia_doenca_atual = st.text_area(
                    "Complemento da queixa / história atual",
                    placeholder="Use apenas se precisar detalhar algo importante.",
                )

                sintomas_lista = st.multiselect("Sintomas", SINTOMAS)
                sintomas_outros = st.text_input("Outros sintomas", placeholder="Opcional")

                st.subheader("2. Histórico clínico")
                historia_patologica_lista = st.multiselect("História patológica pregressa", HISTORIA_PATOLOGICA)
                historia_familiar_lista = st.multiselect("História familiar", HISTORIA_FAMILIAR_OPCOES)

                col_h1, col_h2, col_h3 = st.columns(3)
                with col_h1:
                    numero_filhos_idades = st.text_input("Nº de filhos e idades")
                with col_h2:
                    amamentou = st.selectbox("Amamentou?", SIM_NAO)
                with col_h3:
                    tratamento_nutricional_anterior = st.selectbox("Tratamento nutricional anterior?", SIM_NAO)

                qual_tratamento = st.text_input("Qual tratamento anterior?", placeholder="Opcional")
                internacoes_cirurgias = st.text_area("Internações/Cirurgias", placeholder="Opcional")
                medicamentos_suplementos = st.text_area("Medicamentos/Suplementos em uso", placeholder="Opcional")

                st.subheader("3. Hábitos e dados clínicos")
                col1, col2, col3 = st.columns(3)
                with col1:
                    atividade_fisica = st.selectbox("Atividade física", ATIVIDADE_FISICA_TIPO)
                    frequencia_atividade = st.selectbox("Frequência", FREQUENCIA_SEMANAL)
                    horario_atividade_fisica = st.selectbox("Horário", PERIODO_DIA)
                with col2:
                    consumo_alcool = st.selectbox("Consumo de álcool", CONSUMO_ALCOOL)
                    tabagismo = st.selectbox("Tabagismo", TABAGISMO)
                    qualidade_sono = st.selectbox("Qualidade do sono", QUALIDADE_SONO)
                with col3:
                    hora_acordar = st.time_input("Hora de acordar", value=None)
                    hora_dormir = st.time_input("Hora de dormir", value=None)
                    disposicao_fisica = st.selectbox("Disposição física/energia", DISPOSICAO)

                col4, col5 = st.columns(2)
                with col4:
                    funcionamento_intestinal = st.selectbox("Funcionamento intestinal", FUNCIONAMENTO_INTESTINAL)
                with col5:
                    funcionamento_urinario = st.selectbox("Funcionamento urinário", FUNCIONAMENTO_URINARIO)

                st.subheader("4. Dados alimentares")
                col6, col7, col8 = st.columns(3)
                with col6:
                    intolerancia_alergia_lista = st.multiselect(
                        "Intolerância/Alergia alimentar",
                        [
                            "Nenhuma",
                            "Lactose",
                            "Glúten",
                            "Leite",
                            "Ovo",
                            "Amendoim/castanhas",
                            "Frutos do mar",
                            "Corantes/conservantes",
                            "Outra",
                        ],
                    )
                    denticao = st.selectbox("Dentição", DENTICAO)
                    mastigacao = st.selectbox("Mastigação", MASTIGACAO)
                with col7:
                    quem_cozinha = st.selectbox("Quem cozinha?", QUEM_COZINHA)
                    apetite = st.selectbox("Apetite", APETITE)
                    horario_mais_fome = st.selectbox("Horário de mais fome", PERIODO_DIA)
                with col8:
                    ingestao_agua_dia = st.selectbox("Ingestão de água/dia", INGESTAO_AGUA)
                    habito_beliscar = st.selectbox("Hábito de beliscar?", SIM_NAO_EVENTUAL)
                    refeicoes_habituais = st.multiselect("Refeições habituais", REFEICOES)

                alimentos_preferidos_lista = st.multiselect("Grupos/alimentos mais consumidos", GRUPOS_ALIMENTARES)
                alimentos_preferidos_obs = st.text_input("Alimentos preferidos específicos", placeholder="Opcional")
                alimentos_que_nao_gosta = st.text_input("Alimentos que não gosta", placeholder="Opcional")
                habitos_fim_de_semana_lista = st.multiselect("Hábitos de fim de semana", HABITOS_FIM_SEMANA)

                observacoes_finais = st.text_area("Observações finais", placeholder="Campo livre apenas para informações relevantes.")

                submitted = st.form_submit_button("Salvar anamnese guiada", type="primary")

                if submitted:
                    sintomas = csv_multiselect(sintomas_lista + ([sintomas_outros] if sintomas_outros else []))
                    historia_patologica_pregressa = csv_multiselect(historia_patologica_lista)
                    historia_familiar = csv_multiselect(historia_familiar_lista)
                    intolerancia_alergia_alimentar = csv_multiselect(intolerancia_alergia_lista)
                    habitos_fim_de_semana = csv_multiselect(habitos_fim_de_semana_lista)
                    alimentos_preferidos = csv_multiselect(alimentos_preferidos_lista + ([alimentos_preferidos_obs] if alimentos_preferidos_obs else []))

                    atividade_fisica_final = " | ".join([x for x in [atividade_fisica, frequencia_atividade] if x])
                    hora_acordar_txt = hora_acordar.strftime("%H:%M") if hora_acordar else ""
                    hora_dormir_txt = hora_dormir.strftime("%H:%M") if hora_dormir else ""

                    resultado = cadastrar_anamnese({
                        "paciente_id": paciente_id,
                        "data_anamnese": data_anamnese,
                        "queixa_principal": queixa_principal,
                        "historia_doenca_atual": historia_doenca_atual,
                        "sintomas": sintomas,
                        "historia_patologica_pregressa": historia_patologica_pregressa,
                        "historia_familiar": historia_familiar,
                        "numero_filhos_idades": numero_filhos_idades,
                        "amamentou": amamentou,
                        "atividade_fisica": atividade_fisica_final,
                        "horario_atividade_fisica": horario_atividade_fisica,
                        "consumo_alcool": consumo_alcool,
                        "tabagismo": tabagismo,
                        "qualidade_sono": qualidade_sono,
                        "hora_acordar": hora_acordar_txt,
                        "hora_dormir": hora_dormir_txt,
                        "comportamento_peso": comportamento_peso,
                        "disposicao_fisica": disposicao_fisica,
                        "funcionamento_intestinal": funcionamento_intestinal,
                        "funcionamento_urinario": funcionamento_urinario,
                        "internacoes_cirurgias": internacoes_cirurgias,
                        "medicamentos_suplementos": medicamentos_suplementos,
                        "intolerancia_alergia_alimentar": intolerancia_alergia_alimentar,
                        "denticao": denticao,
                        "mastigacao": mastigacao,
                        "quem_cozinha": quem_cozinha,
                        "apetite": apetite,
                        "horario_mais_fome": horario_mais_fome,
                        "ingestao_agua_dia": ingestao_agua_dia,
                        "tratamento_nutricional_anterior": tratamento_nutricional_anterior,
                        "qual_tratamento": qual_tratamento,
                        "alimentos_preferidos": alimentos_preferidos,
                        "habito_beliscar": habito_beliscar,
                        "alimentos_que_nao_gosta": alimentos_que_nao_gosta,
                        "habitos_fim_de_semana": habitos_fim_de_semana,
                        "observacoes": observacoes_finais,
                        "refeicoes_habituais": csv_multiselect(refeicoes_habituais),
                    })
                    if resultado["sucesso"]:
                        st.success("Anamnese guiada cadastrada com sucesso.")
                    else:
                        for erro in resultado["erros"]:
                            st.error(erro)

    with aba_recordatorio:
        paciente_id = selecionar_paciente("Paciente", key="anamnese_paciente_recordatorio")
        if paciente_id:
            with st.form("form_recordatorio_guiado", clear_on_submit=True):
                data_registro = st.text_input("Data do registro", placeholder="AAAA-MM-DD; vazio = hoje")

                st.caption("Use os campos principais e marque características do padrão alimentar.")
                colr1, colr2 = st.columns(2)
                with colr1:
                    desjejum = st.text_area("Café da manhã")
                    lanche_manha = st.text_area("Lanche da manhã")
                    almoco = st.text_area("Almoço")
                with colr2:
                    lanche_tarde = st.text_area("Lanche da tarde")
                    jantar = st.text_area("Jantar")
                    ceia = st.text_area("Ceia")

                padrao_refeicoes = st.multiselect(
                    "Características do recordatório",
                    [
                        "Pula café da manhã",
                        "Baixa ingestão de água",
                        "Baixo consumo de frutas",
                        "Baixo consumo de verduras/legumes",
                        "Alto consumo de doces",
                        "Alto consumo de ultraprocessados",
                        "Alto consumo de frituras",
                        "Alto consumo de refrigerantes/sucos artificiais",
                        "Beliscos frequentes",
                        "Longo intervalo sem comer",
                        "Horários irregulares",
                    ],
                )
                observacoes = st.text_area("Observações")

                submitted = st.form_submit_button("Salvar recordatório", type="primary")

                if submitted:
                    obs_final = observacoes
                    if padrao_refeicoes:
                        obs_final = f"{observacoes}\nPadrões marcados: {csv_multiselect(padrao_refeicoes)}".strip()

                    resultado = cadastrar_recordatorio({
                        "paciente_id": paciente_id,
                        "data_registro": data_registro,
                        "desjejum": desjejum,
                        "lanche_manha": lanche_manha,
                        "almoco": almoco,
                        "lanche_tarde": lanche_tarde,
                        "jantar": jantar,
                        "ceia": ceia,
                        "observacoes": obs_final,
                    })
                    if resultado["sucesso"]:
                        st.success("Recordatório cadastrado com sucesso.")
                    else:
                        for erro in resultado["erros"]:
                            st.error(erro)

    with aba_historico:
        paciente_id = selecionar_paciente("Paciente", key="anamnese_paciente_historico")
        if paciente_id:
            st.subheader("Anamneses")
            mostrar_dataframe(pd.DataFrame(listar_anamneses_por_paciente(paciente_id)), "Sem anamnese cadastrada.")
            st.subheader("Recordatórios")
            mostrar_dataframe(pd.DataFrame(listar_recordatorios_por_paciente(paciente_id)), "Sem recordatório cadastrado.")

    with aba_resumo:
        paciente_id = selecionar_paciente("Paciente", key="anamnese_paciente_resumo")
        if paciente_id:
            resumo = gerar_resumo_nutricional_paciente(paciente_id)
            st.write(resumo.get("resumo"))
            for ponto in resumo.get("pontos_atencao", []):
                st.warning(ponto)

import pandas as pd
import streamlit as st

from src.anamnese import (
    cadastrar_anamnese,
    cadastrar_recordatorio,
    listar_anamneses_por_paciente,
    listar_recordatorios_por_paciente,
    gerar_resumo_nutricional_paciente,
)
from src.web.common import selecionar_paciente, mostrar_dataframe
from src.web.styles import header


def render():
    header("📝 Anamnese", "Registro clínico-nutricional, hábitos alimentares e recordatório habitual.")

    aba_anamnese, aba_recordatorio, aba_historico, aba_resumo = st.tabs([
        "Anamnese",
        "Recordatório",
        "Histórico",
        "Resumo",
    ])

    with aba_anamnese:
        paciente_id = selecionar_paciente("Paciente")
        if paciente_id:
            with st.form("form_anamnese", clear_on_submit=True):
                st.subheader("Identificação clínica")
                data_anamnese = st.text_input("Data da anamnese", placeholder="AAAA-MM-DD; vazio = hoje")
                queixa_principal = st.text_area("Queixa principal")
                historia_doenca_atual = st.text_area("História da doença atual")
                sintomas = st.text_area("Sintomas")
                historia_patologica_pregressa = st.text_area("História patológica pregressa")
                historia_familiar = st.text_area("História familiar")

                col1, col2 = st.columns(2)
                with col1:
                    numero_filhos_idades = st.text_input("Nº de filhos e idades")
                    amamentou = st.selectbox("Amamentou?", ["", "Sim", "Não"])
                    atividade_fisica = st.text_input("Atividade física")
                    horario_atividade_fisica = st.text_input("Horário da atividade física")
                    consumo_alcool = st.text_input("Consumo de álcool")
                    tabagismo = st.text_input("Tabagismo")
                    qualidade_sono = st.text_input("Qualidade do sono")
                    hora_acordar = st.text_input("Hora de acordar")
                    hora_dormir = st.text_input("Hora de dormir")
                with col2:
                    comportamento_peso = st.text_input("Comportamento do peso")
                    disposicao_fisica = st.text_input("Disposição física/energia")
                    funcionamento_intestinal = st.text_input("Funcionamento intestinal")
                    funcionamento_urinario = st.text_input("Funcionamento urinário")
                    internacoes_cirurgias = st.text_area("Internações/Cirurgias")
                    medicamentos_suplementos = st.text_area("Medicamentos/Suplementos")
                    intolerancia_alergia_alimentar = st.text_area("Intolerância/Alergia alimentar")

                st.subheader("Dados alimentares")
                col3, col4 = st.columns(2)
                with col3:
                    denticao = st.text_input("Dentição")
                    mastigacao = st.text_input("Mastigação")
                    quem_cozinha = st.text_input("Quem cozinha")
                    apetite = st.text_input("Apetite")
                    horario_mais_fome = st.text_input("Horário de mais fome")
                    ingestao_agua_dia = st.text_input("Ingestão de água/dia")
                with col4:
                    tratamento_nutricional_anterior = st.selectbox("Tratamento nutricional anterior?", ["", "Sim", "Não"])
                    qual_tratamento = st.text_input("Qual tratamento")
                    alimentos_preferidos = st.text_area("Alimentos preferidos")
                    habito_beliscar = st.selectbox("Hábito de beliscar?", ["", "Sim", "Não"])
                    alimentos_que_nao_gosta = st.text_area("Alimentos que não gosta")
                    habitos_fim_de_semana = st.text_area("Hábitos de fim de semana")

                submitted = st.form_submit_button("Salvar anamnese", type="primary")

                if submitted:
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
                        "atividade_fisica": atividade_fisica,
                        "horario_atividade_fisica": horario_atividade_fisica,
                        "consumo_alcool": consumo_alcool,
                        "tabagismo": tabagismo,
                        "qualidade_sono": qualidade_sono,
                        "hora_acordar": hora_acordar,
                        "hora_dormir": hora_dormir,
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
                    })
                    if resultado["sucesso"]:
                        st.success("Anamnese cadastrada com sucesso.")
                    else:
                        for erro in resultado["erros"]:
                            st.error(erro)

    with aba_recordatorio:
        paciente_id = selecionar_paciente("Paciente")
        if paciente_id:
            with st.form("form_recordatorio", clear_on_submit=True):
                data_registro = st.text_input("Data do registro", placeholder="AAAA-MM-DD; vazio = hoje")
                desjejum = st.text_area("Desjejum")
                lanche_manha = st.text_area("Lanche da manhã")
                almoco = st.text_area("Almoço")
                lanche_tarde = st.text_area("Lanche da tarde")
                jantar = st.text_area("Jantar")
                ceia = st.text_area("Ceia")
                observacoes = st.text_area("Observações")
                submitted = st.form_submit_button("Salvar recordatório", type="primary")

                if submitted:
                    resultado = cadastrar_recordatorio({
                        "paciente_id": paciente_id,
                        "data_registro": data_registro,
                        "desjejum": desjejum,
                        "lanche_manha": lanche_manha,
                        "almoco": almoco,
                        "lanche_tarde": lanche_tarde,
                        "jantar": jantar,
                        "ceia": ceia,
                        "observacoes": observacoes,
                    })
                    if resultado["sucesso"]:
                        st.success("Recordatório cadastrado com sucesso.")
                    else:
                        for erro in resultado["erros"]:
                            st.error(erro)

    with aba_historico:
        paciente_id = selecionar_paciente("Paciente")
        if paciente_id:
            st.subheader("Anamneses")
            mostrar_dataframe(pd.DataFrame(listar_anamneses_por_paciente(paciente_id)), "Sem anamnese cadastrada.")
            st.subheader("Recordatórios")
            mostrar_dataframe(pd.DataFrame(listar_recordatorios_por_paciente(paciente_id)), "Sem recordatório cadastrado.")

    with aba_resumo:
        paciente_id = selecionar_paciente("Paciente")
        if paciente_id:
            resumo = gerar_resumo_nutricional_paciente(paciente_id)
            st.write(resumo.get("resumo"))
            for ponto in resumo.get("pontos_atencao", []):
                st.warning(ponto)

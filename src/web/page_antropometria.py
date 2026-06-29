import pandas as pd
import streamlit as st

from src.antropometria import (
    cadastrar_antropometria,
    listar_antropometrias_por_paciente,
    calcular_evolucao_antropometrica,
    preparar_series_graficos_antropometria,
)
from src.web.common import selecionar_paciente, mostrar_dataframe
from src.web.styles import header
from src.web.navigation import avancar_fluxo, mostrar_proxima_etapa


def render():
    header("📏 Antropometria", "Registro de peso, altura, IMC, cintura e evolução corporal.")

    aba_cadastro, aba_historico, aba_evolucao = st.tabs(["Cadastrar", "Histórico", "Evolução"])

    with aba_cadastro:
        paciente_id = selecionar_paciente("Paciente")
        if paciente_id:
            with st.form("form_antropometria", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    data_avaliacao = st.text_input("Data da avaliação", placeholder="AAAA-MM-DD; vazio = hoje")
                    peso = st.text_input("Peso em kg")
                    altura = st.text_input("Altura em metros ou cm", placeholder="Ex.: 1,70 ou 170")
                with col2:
                    circunferencia_cintura = st.text_input("Circunferência da cintura em cm")
                    observacoes = st.text_area("Observações")

                submitted = st.form_submit_button("Salvar avaliação", type="primary")

                if submitted:
                    resultado = cadastrar_antropometria({
                        "paciente_id": paciente_id,
                        "data_avaliacao": data_avaliacao,
                        "peso": peso,
                        "altura": altura,
                        "circunferencia_cintura": circunferencia_cintura,
                        "observacoes": observacoes,
                    })
                    if resultado["sucesso"]:
                        ant = resultado["antropometria"]
                        st.success(f"Avaliação salva. IMC: {ant.get('imc')} | {ant.get('classificacao_imc')}")
                    else:
                        for erro in resultado["erros"]:
                            st.error(erro)

    with aba_historico:
        paciente_id = selecionar_paciente("Paciente")
        if paciente_id:
            mostrar_dataframe(pd.DataFrame(listar_antropometrias_por_paciente(paciente_id)), "Sem avaliações cadastradas.")

    with aba_evolucao:
        paciente_id = selecionar_paciente("Paciente")
        if paciente_id:
            evolucao = calcular_evolucao_antropometrica(paciente_id)
            if not evolucao.get("possui_dados"):
                st.info(evolucao.get("resumo"))
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Peso atual", evolucao.get("peso_atual"), evolucao.get("delta_peso"))
                c2.metric("IMC atual", evolucao.get("imc_atual"), evolucao.get("delta_imc"))
                c3.metric("Cintura atual", evolucao.get("cintura_atual"), evolucao.get("delta_cintura"))

                series = preparar_series_graficos_antropometria(paciente_id)
                df = pd.DataFrame(series)
                if not df.empty:
                    df = df.set_index("datas")
                    st.line_chart(df[["pesos", "imcs", "cinturas"]])

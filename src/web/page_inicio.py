import pandas as pd
import streamlit as st

from src.dashboard import gerar_indicadores_gerais
from src.web.styles import header, card_info


def render():
    header("🥗 NutriSoft", "Gestão nutricional local com CSV, análise comparativa, dashboards e gráficos.")

    card_info(
        "O NutriSoft é uma ferramenta de apoio à análise profissional. "
        "Ele não substitui diagnóstico, prescrição ou conduta clínica individualizada."
    )

    indicadores = gerar_indicadores_gerais()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Pacientes", indicadores.get("total_pacientes", 0))
    c2.metric("Anamneses", indicadores.get("total_anamneses", 0))
    c3.metric("Antropometrias", indicadores.get("total_avaliacoes_antropometricas", 0))
    c4.metric("Exames", indicadores.get("total_exames", 0))
    c5.metric("Com alterações", indicadores.get("pacientes_com_exames_alterados", 0))

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Distribuição por status dos exames")
        dist = indicadores.get("distribuicao_status_exames", {})
        if dist:
            df = pd.DataFrame([{"Status": k, "Quantidade": v} for k, v in dist.items()])
            st.bar_chart(df.set_index("Status"))
        else:
            st.info("Ainda não há análises de exames.")

    with col_b:
        st.subheader("Exames mais alterados")
        alterados = indicadores.get("exames_mais_alterados", {})
        if alterados:
            df = pd.DataFrame([{"Exame": k, "Quantidade": v} for k, v in alterados.items()])
            st.bar_chart(df.set_index("Exame"))
        else:
            st.info("Ainda não há exames alterados identificados.")

    st.divider()
    st.subheader("Fluxo recomendado")
    st.write(
        "1. Cadastrar paciente → 2. Cadastrar anamnese → 3. Registrar antropometria → "
        "4. Registrar exames → 5. Executar análise → 6. Consultar dashboard."
    )

import pandas as pd
import streamlit as st

from src.dashboard import gerar_indicadores_gerais
from src.completude import listar_completude_pacientes
from src.web.styles import header, card_info


def render():
    header("🥗 NutriSoft", "Gestão nutricional local, limpa e orientada à análise.")

    indicadores = gerar_indicadores_gerais()
    completude = pd.DataFrame(listar_completude_pacientes())

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Pacientes", indicadores.get("total_pacientes", 0))
    c2.metric("Anamneses", indicadores.get("total_anamneses", 0))
    c3.metric("Antropometrias", indicadores.get("total_avaliacoes_antropometricas", 0))
    c4.metric("Exames", indicadores.get("total_exames", 0))
    media = f"{completude['percentual'].mean():.1f}%" if not completude.empty else "0%"
    c5.metric("Completude média", media)

    card_info(
        "Fluxo recomendado: Pacientes → Anamnese → Antropometria → Exames → Dashboard. "
        "Use a página Completude para verificar rapidamente se o cadastro está aceitável."
    )

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Completude dos cadastros")
        if not completude.empty:
            st.bar_chart(completude.set_index("nome")[["percentual"]], height=330)
        else:
            st.info("Cadastre pacientes para visualizar a completude.")

    with col_b:
        st.subheader("Distribuição dos exames por status")
        dist = indicadores.get("distribuicao_status_exames", {})
        if dist:
            df = pd.DataFrame([{"Status": k, "Quantidade": v} for k, v in dist.items()])
            st.bar_chart(df.set_index("Status"), height=330)
        else:
            st.info("Ainda não há análises de exames.")

    st.divider()
    st.subheader("Atalhos de uso")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**1. Cadastro**")
        st.write("Inclua dados básicos e acompanhe completude.")
    with col2:
        st.markdown("**2. Análise**")
        st.write("Cadastre exames, referências e execute análise.")
    with col3:
        st.markdown("**3. Relatório**")
        st.write("Gere PDF e acompanhe evolução em tela.")

import streamlit as st

from src.web.common import df_csv, mostrar_dataframe
from src.web.styles import header


def render():
    header("🗂️ Bases CSV", "Consulta técnica das bases locais utilizadas pelo NutriSoft.")

    nomes = [
        "pacientes",
        "anamnese",
        "recordatorio_habitual",
        "antropometria",
        "exames",
        "referencias_exames",
        "alias_exames",
        "analise_exames",
        "evolucao_conduta",
    ]

    nome = st.selectbox("Selecione a base", nomes)
    df = df_csv(nome)

    st.caption(f"Base selecionada: data/{nome}.csv")
    mostrar_dataframe(df, "Base vazia.")

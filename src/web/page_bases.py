import streamlit as st

from src.exportacao import enriquecer_com_nome_paciente, csv_bytes_com_nome_paciente
from src.web.common import mostrar_dataframe
from src.web.styles import header


def render():
    header("🗂️ Bases CSV", "Consulta e exportação das bases locais, com nome do paciente quando aplicável.")

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
        "historico_edicoes",
    ]

    nome = st.selectbox("Selecione a base", nomes)
    df = enriquecer_com_nome_paciente(nome)

    st.caption(f"Base selecionada: data/{nome}.csv")
    mostrar_dataframe(df, "Base vazia.")

    st.download_button(
        "Baixar CSV enriquecido",
        data=csv_bytes_com_nome_paciente(nome),
        file_name=f"{nome}_com_nome_paciente.csv",
        mime="text/csv",
        type="primary",
    )

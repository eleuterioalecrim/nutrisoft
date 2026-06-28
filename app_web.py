import streamlit as st

from src.database import inicializar_banco_csv
from src.web.styles import aplicar_estilo_global
from src.web import (
    page_inicio,
    page_pacientes,
    page_anamnese,
    page_antropometria,
    page_exames,
    page_dashboard,
    page_bases,
)


st.set_page_config(
    page_title="NutriSoft",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    inicializar_banco_csv()
    aplicar_estilo_global()

    st.sidebar.title("🥗 NutriSoft")
    st.sidebar.caption("Interface web local")
    st.sidebar.divider()

    pagina = st.sidebar.radio(
        "Navegação",
        [
            "Início",
            "Pacientes",
            "Anamnese",
            "Antropometria",
            "Exames",
            "Dashboard",
            "Bases CSV",
        ],
    )

    st.sidebar.divider()
    st.sidebar.caption("Banco local: CSV")
    st.sidebar.caption("Interface: Streamlit")

    if pagina == "Início":
        page_inicio.render()
    elif pagina == "Pacientes":
        page_pacientes.render()
    elif pagina == "Anamnese":
        page_anamnese.render()
    elif pagina == "Antropometria":
        page_antropometria.render()
    elif pagina == "Exames":
        page_exames.render()
    elif pagina == "Dashboard":
        page_dashboard.render()
    elif pagina == "Bases CSV":
        page_bases.render()


if __name__ == "__main__":
    main()

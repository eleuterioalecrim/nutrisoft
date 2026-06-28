import pandas as pd
import streamlit as st

from src.dashboard import gerar_indicadores_gerais, gerar_dashboard_paciente
from src.graficos import gerar_todos_graficos_paciente
from src.web.common import selecionar_paciente
from src.web.styles import header, card_alerta


def render():
    header("📊 Dashboard", "Visão executiva do paciente, exames alterados e evolução nutricional.")

    aba_geral, aba_paciente, aba_graficos = st.tabs(["Geral", "Paciente", "Gerar PNG"])

    with aba_geral:
        indicadores = gerar_indicadores_gerais()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Pacientes", indicadores.get("total_pacientes", 0))
        c2.metric("Anamneses", indicadores.get("total_anamneses", 0))
        c3.metric("Antropometrias", indicadores.get("total_avaliacoes_antropometricas", 0))
        c4.metric("Exames", indicadores.get("total_exames", 0))
        c5.metric("Com alterações", indicadores.get("pacientes_com_exames_alterados", 0))

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Status dos exames")
            dist = indicadores.get("distribuicao_status_exames", {})
            if dist:
                df = pd.DataFrame([{"Status": k, "Quantidade": v} for k, v in dist.items()])
                st.bar_chart(df.set_index("Status"))
            else:
                st.info("Sem dados de análise.")
        with col2:
            st.subheader("Exames mais alterados")
            alterados = indicadores.get("exames_mais_alterados", {})
            if alterados:
                df = pd.DataFrame([{"Exame": k, "Quantidade": v} for k, v in alterados.items()])
                st.bar_chart(df.set_index("Exame"))
            else:
                st.info("Sem exames alterados.")

    with aba_paciente:
        paciente_id = selecionar_paciente("Paciente")
        if paciente_id:
            r = gerar_dashboard_paciente(paciente_id)
            if not r["sucesso"]:
                st.error(r["erro"])
            else:
                d = r["dashboard"]
                paciente = d["paciente"]
                st.subheader(f"{paciente.get('nome', '')} | ID {paciente.get('paciente_id', '')}")

                col1, col2, col3, col4 = st.columns(4)
                antrop = d.get("antropometria_atual") or {}
                col1.metric("Peso", antrop.get("peso", "-"))
                col2.metric("IMC", antrop.get("imc", "-"))
                col3.metric("Cintura", antrop.get("circunferencia_cintura", "-"))
                col4.metric("Alertas", len(d.get("alertas", [])))

                st.subheader("Alertas")
                alertas = d.get("alertas", [])
                if alertas:
                    for alerta in alertas:
                        card_alerta(alerta)
                else:
                    st.success("Nenhum alerta automático no momento.")

                st.subheader("Resumo de exames")
                st.info(d.get("resumo_exames", {}).get("resumo", ""))

                exames_alterados = d.get("exames_alterados", [])
                if exames_alterados:
                    st.subheader("Exames alterados ou pendentes")
                    st.dataframe(pd.DataFrame(exames_alterados), width='stretch', hide_index=True)

    with aba_graficos:
        paciente_id = selecionar_paciente("Paciente")
        if paciente_id:
            if st.button("Gerar gráficos PNG", type="primary"):
                resultados = gerar_todos_graficos_paciente(paciente_id)
                for nome, info in resultados.items():
                    if info["sucesso"]:
                        st.success(f"{nome}: {info['arquivo']}")
                    else:
                        st.warning(f"{nome}: {info['erro']}")

            st.info("Os arquivos são salvos em `reports/charts/`.")

import pandas as pd
import streamlit as st

from src.completude import calcular_completude_paciente, listar_completude_pacientes
from src.web.common import selecionar_paciente, mostrar_dataframe
from src.web.styles import header, completion_box, status_pill, card_info


def _tipo_nivel(nivel: str) -> str:
    if nivel == "Completo":
        return "success"
    if nivel == "Aceitável":
        return "warning"
    return "danger"


def render():
    header("📈 Completude do paciente", "Indicador rápido de maturidade das informações cadastradas.")

    aba_geral, aba_paciente = st.tabs(["Visão geral", "Paciente"])

    with aba_geral:
        card_info(
            "A completude mede se há dados suficientes para acompanhamento: cadastro, anamnese, "
            "recordatório, antropometria, exames e análise comparativa."
        )

        df = pd.DataFrame(listar_completude_pacientes())
        if df.empty:
            st.info("Nenhum paciente cadastrado.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Pacientes avaliados", len(df))
            c2.metric("Média de completude", f"{df['percentual'].mean():.1f}%")
            c3.metric("Abaixo de 65%", int((df["percentual"] < 65).sum()))

            st.subheader("Ranking de completude")
            mostrar_dataframe(df, "Sem dados.")
            st.bar_chart(df.set_index("nome")[["percentual"]], height=360)

    with aba_paciente:
        paciente_id = selecionar_paciente("Paciente", key="completude_paciente")
        if paciente_id:
            c = calcular_completude_paciente(paciente_id)

            col_a, col_b = st.columns([2, 1])
            with col_a:
                completion_box(
                    f"Completude geral: {c['nivel']}",
                    c["descricao"],
                    c["percentual"],
                )
            with col_b:
                st.metric("Percentual", f"{c['percentual']:.1f}%")
                status_pill(c["nivel"], _tipo_nivel(c["nivel"]))

            st.subheader("Completude por bloco")
            blocos = c.get("blocos", {})
            df_blocos = pd.DataFrame([
                {
                    "Bloco": bloco,
                    "Percentual": dados["percentual"],
                    "Preenchidos": dados["preenchidos"],
                    "Total": dados["total"],
                    "Peso": dados["peso"],
                }
                for bloco, dados in blocos.items()
            ])
            mostrar_dataframe(df_blocos, "Sem blocos.")
            if not df_blocos.empty:
                st.bar_chart(df_blocos.set_index("Bloco")[["Percentual"]], height=320)

            st.subheader("Pendências")
            pendencias = c.get("pendencias", [])
            if pendencias:
                for p in pendencias:
                    st.warning(p)
            else:
                st.success("Cadastro com informações suficientes para acompanhamento.")

import pandas as pd
import streamlit as st

from src.dashboard import gerar_indicadores_gerais, gerar_dashboard_paciente
from src.interpretacao_exames import gerar_insights_exames_paciente
from src.relatorio_pdf import gerar_pdf_analise_paciente
from src.antropometria import preparar_series_graficos_antropometria
from src.web.common import selecionar_paciente, mostrar_dataframe
from src.completude import calcular_completude_paciente
from src.web.styles import header, card_alerta, card_info, completion_box


def _df_from_dict(dados: dict, col_item: str = "Item", col_valor: str = "Quantidade") -> pd.DataFrame:
    if not dados:
        return pd.DataFrame(columns=[col_item, col_valor])
    df = pd.DataFrame([{col_item: k, col_valor: v} for k, v in dados.items()])
    df[col_valor] = pd.to_numeric(df[col_valor], errors="coerce").fillna(0)
    return df


def _grafico_barras(titulo: str, dados: dict, col_item: str = "Item", col_valor: str = "Quantidade"):
    st.subheader(titulo)
    df = _df_from_dict(dados, col_item, col_valor)
    if df.empty or df[col_valor].sum() == 0:
        st.info("Sem dados para exibir. Cadastre exames e execute a análise comparativa.")
        return
    st.bar_chart(df.set_index(col_item), height=280)


def _grafico_prioridades(prioridades: list[dict]):
    st.subheader("Prioridade por painel")
    if not prioridades:
        st.success("Nenhum painel com prioridade automática no momento.")
        return

    df = pd.DataFrame(prioridades)
    if df.empty or "painel" not in df.columns or "score" not in df.columns:
        st.info("Sem dados suficientes para o gráfico de prioridade.")
        return

    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)
    mostrar_dataframe(df, "Sem prioridades.")
    if df["score"].sum() > 0:
        st.bar_chart(df.set_index("painel")[["score"]], height=280)
    else:
        st.info("Sem pontuação de prioridade para renderizar.")


def _grafico_evolucao_antropometrica(paciente_id: str):
    st.subheader("Evolução antropométrica")
    series = preparar_series_graficos_antropometria(paciente_id)
    df = pd.DataFrame(series)

    if df.empty or "datas" not in df.columns:
        st.info("Sem dados suficientes para gráfico de evolução.")
        return

    df = df.set_index("datas")
    colunas = []
    mapa = {
        "pesos": "Peso",
        "imcs": "IMC",
        "cinturas": "Cintura",
    }

    for origem, destino in mapa.items():
        if origem in df.columns:
            df[destino] = pd.to_numeric(df[origem], errors="coerce")
            colunas.append(destino)

    if not colunas or df[colunas].dropna(how="all").empty:
        st.info("Sem dados numéricos suficientes para gráfico de evolução.")
        return

    st.line_chart(df[colunas], height=320)


def _grafico_status_paciente(insights: dict):
    st.subheader("Distribuição dos exames do paciente")
    status = insights.get("status", {})
    df = _df_from_dict(status, "Status", "Quantidade")

    if df.empty or df["Quantidade"].sum() == 0:
        st.info("Sem exames analisados. Vá em Exames → Análise orientada → Executar análise comparativa.")
        return

    st.bar_chart(df.set_index("Status"), height=280)


def _alertas_exames(insights: dict):
    st.subheader("Alertas interpretativos")
    alertas = insights.get("alertas", [])

    if not alertas:
        st.success("Nenhum alerta automático com base nas referências cadastradas.")
        return

    for alerta in alertas:
        card_alerta(f"<b>{alerta['tipo']} | {alerta['painel']}</b><br>{alerta['mensagem']}")


def _botao_pdf(paciente_id: str, contexto: str):
    st.subheader("Relatório PDF para impressão")
    st.write(
        "Gere um relatório com dados do paciente, anamnese recente, antropometria, "
        "resumo dos exames, prioridades e recomendações de fluxo."
    )

    key_botao = f"pdf_{contexto}_{paciente_id}"
    key_download = f"download_pdf_{contexto}_{paciente_id}"

    if st.button("📄 Gerar PDF da análise do paciente", type="primary", key=key_botao):
        pdf = gerar_pdf_analise_paciente(paciente_id)

        if pdf["sucesso"]:
            st.success(f"PDF gerado com sucesso: {pdf['arquivo']}")
            with open(pdf["arquivo"], "rb") as f:
                st.download_button(
                    "⬇️ Baixar PDF",
                    data=f.read(),
                    file_name=pdf["arquivo"].split("/")[-1],
                    mime="application/pdf",
                    key=key_download,
                )
        else:
            st.error(pdf["erro"])


def _aviso_pre_requisitos():
    card_info(
        "Para os gráficos aparecerem com dados, siga este fluxo: "
        "1) cadastre o paciente, 2) cadastre exames, 3) carregue referências padrão em "
        "Exames → Referências, 4) execute a análise em Exames → Análise orientada."
    )


def render():
    header("📊 Dashboard clínico-nutricional", "Gráficos em tela, análise por painéis e relatório PDF para impressão.")

    aba_geral, aba_paciente, aba_pdf = st.tabs([
        "Visão geral",
        "Painel do paciente",
        "Relatório PDF",
    ])

    with aba_geral:
        indicadores = gerar_indicadores_gerais()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Pacientes", indicadores.get("total_pacientes", 0))
        c2.metric("Anamneses", indicadores.get("total_anamneses", 0))
        c3.metric("Antropometrias", indicadores.get("total_avaliacoes_antropometricas", 0))
        c4.metric("Exames", indicadores.get("total_exames", 0))
        c5.metric("Com alterações", indicadores.get("pacientes_com_exames_alterados", 0))

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            _grafico_barras(
                "Distribuição dos exames por status",
                indicadores.get("distribuicao_status_exames", {}),
                "Status",
                "Quantidade",
            )
        with col2:
            _grafico_barras(
                "Exames mais alterados",
                indicadores.get("exames_mais_alterados", {}),
                "Exame",
                "Quantidade",
            )

        _aviso_pre_requisitos()

    with aba_paciente:
        paciente_id = selecionar_paciente("Paciente", key="dashboard_paciente_principal")

        if paciente_id:
            r = gerar_dashboard_paciente(paciente_id)
            insights = gerar_insights_exames_paciente(paciente_id)

            if not r["sucesso"]:
                st.error(r["erro"])
                return

            d = r["dashboard"]
            paciente = d["paciente"]
            antrop = d.get("antropometria_atual") or {}

            st.subheader(f"{paciente.get('nome', '')} | ID {paciente.get('paciente_id', '')}")

            st.markdown("### 1. Indicadores atuais")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Peso", antrop.get("peso", "-"))
            col2.metric("IMC", antrop.get("imc", "-"))
            col3.metric("Classificação IMC", antrop.get("classificacao_imc", "-"))
            col4.metric("Cintura", antrop.get("circunferencia_cintura", "-"))
            col5.metric("Alertas", len(insights.get("alertas", [])))

            st.markdown("### 2. Resumo executivo")
            st.info(insights.get("resumo_executivo", "Sem resumo disponível."))

            st.markdown("### 3. Gráficos de análise")
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                _grafico_status_paciente(insights)
            with col_g2:
                _grafico_prioridades(insights.get("prioridades", []))

            _grafico_evolucao_antropometrica(paciente_id)

            st.markdown("### 4. Alertas")
            _alertas_exames(insights)

            st.markdown("### 5. Recomendações de fluxo")
            recomendacoes = insights.get("recomendacoes", [])
            if recomendacoes:
                for rec in recomendacoes:
                    st.write(f"- {rec}")
            else:
                st.info("Sem recomendações automáticas no momento.")

            st.markdown("### 6. Relatório")
            _botao_pdf(paciente_id, contexto="painel")

            st.markdown("### 7. Dados de apoio")
            with st.expander("Alertas gerais do dashboard"):
                alertas_gerais = d.get("alertas", [])
                if alertas_gerais:
                    for alerta in alertas_gerais:
                        st.warning(alerta)
                else:
                    st.success("Sem alertas gerais.")

            with st.expander("Exames alterados ou pendentes"):
                exames_alterados = d.get("exames_alterados", [])
                if exames_alterados:
                    st.dataframe(pd.DataFrame(exames_alterados), width="stretch", hide_index=True)
                else:
                    st.success("Sem exames alterados ou pendentes.")

    with aba_pdf:
        paciente_id = selecionar_paciente("Paciente", key="dashboard_paciente_pdf_exclusivo")
        if paciente_id:
            _botao_pdf(paciente_id, contexto="aba_pdf")

            st.divider()
            st.subheader("Onde o arquivo será salvo?")
            st.info("Após gerar, o PDF fica salvo em `reports/pdf/` e também aparece um botão para baixar o arquivo.")

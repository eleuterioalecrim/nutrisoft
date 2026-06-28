import inspect
from pathlib import Path

import pandas as pd
import streamlit as st

from src.database import ler_csv
from src.pacientes import listar_pacientes


def df_csv(nome_base: str) -> pd.DataFrame:
    return pd.DataFrame(ler_csv(nome_base))


def pacientes_options() -> dict:
    pacientes = listar_pacientes()
    return {
        f"{p.get('paciente_id', '')} - {p.get('nome', '')}": p.get("paciente_id", "")
        for p in pacientes
    }


def _gerar_key_automatica(label: str) -> str:
    frame = inspect.stack()[2]
    arquivo = Path(frame.filename).stem
    linha = frame.lineno
    label_limpo = str(label).lower().replace(" ", "_").replace("-", "_")
    return f"select_paciente_{arquivo}_{linha}_{label_limpo}"


def selecionar_paciente(label: str = "Selecione o paciente", key: str | None = None):
    opcoes = pacientes_options()

    if not opcoes:
        st.warning("Nenhum paciente cadastrado. Cadastre um paciente primeiro.")
        return None

    if key is None:
        key = _gerar_key_automatica(label)

    escolha = st.selectbox(label, list(opcoes.keys()), key=key)
    return opcoes.get(escolha)


def mostrar_dataframe(df: pd.DataFrame, mensagem_vazio: str = "Nenhum registro encontrado."):
    if df.empty:
        st.info(mensagem_vazio)
    else:
        st.dataframe(df, width="stretch", hide_index=True)


def status_badge(status: str) -> str:
    status = status or ""
    if status == "Normal":
        return "🟢 Normal"
    if status == "Acima":
        return "🔴 Acima"
    if status == "Abaixo":
        return "🟠 Abaixo"
    if status == "Sem referência":
        return "⚪ Sem referência"
    if status == "Resultado inválido":
        return "⚫ Resultado inválido"
    return f"• {status}"

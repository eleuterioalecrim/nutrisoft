import pandas as pd

from src.database import ler_csv
from src.pacientes import listar_pacientes


def mapa_pacientes() -> dict:
    return {
        str(p.get("paciente_id", "")).strip(): p.get("nome", "")
        for p in listar_pacientes()
    }


def enriquecer_com_nome_paciente(nome_base: str) -> pd.DataFrame:
    df = pd.DataFrame(ler_csv(nome_base))

    if df.empty:
        return df

    if "paciente_id" not in df.columns:
        return df

    nomes = mapa_pacientes()
    df.insert(1, "paciente_nome", df["paciente_id"].astype(str).map(nomes).fillna(""))
    return df


def csv_bytes_com_nome_paciente(nome_base: str) -> bytes:
    df = enriquecer_com_nome_paciente(nome_base)
    return df.to_csv(index=False).encode("utf-8-sig")

from pathlib import Path
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import CHARTS_DIR
from .pacientes import buscar_paciente_por_id
from .antropometria import preparar_series_graficos_antropometria
from .exames import listar_analises_por_paciente, listar_exames_alterados_por_paciente
from .analises import executar_analise_exames


def _nome_arquivo_seguro(texto: str) -> str:
    texto = str(texto or "").strip().lower()
    texto = "".join(c if c.isalnum() else "_" for c in texto)
    while "__" in texto:
        texto = texto.replace("__", "_")
    return texto.strip("_") or "paciente"


def _validar_paciente(paciente_id: str) -> dict:
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        raise ValueError(f"Paciente ID {paciente_id} não encontrado.")
    return paciente


def gerar_grafico_peso(paciente_id: str) -> str:
    paciente = _validar_paciente(paciente_id)
    series = preparar_series_graficos_antropometria(paciente_id)

    datas = series.get("datas", [])
    pesos = series.get("pesos", [])

    if not datas or not any(v is not None for v in pesos):
        raise ValueError("Não há dados de peso suficientes para gerar o gráfico.")

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    arquivo = CHARTS_DIR / f"{_nome_arquivo_seguro(paciente.get('nome'))}_{paciente_id}_peso.png"

    plt.figure(figsize=(10, 5))
    plt.plot(datas, pesos, marker="o")
    plt.title(f"Evolução do peso - {paciente.get('nome', '')}")
    plt.xlabel("Data")
    plt.ylabel("Peso (kg)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(arquivo, dpi=150)
    plt.close()

    return str(arquivo)


def gerar_grafico_imc(paciente_id: str) -> str:
    paciente = _validar_paciente(paciente_id)
    series = preparar_series_graficos_antropometria(paciente_id)

    datas = series.get("datas", [])
    imcs = series.get("imcs", [])

    if not datas or not any(v is not None for v in imcs):
        raise ValueError("Não há dados de IMC suficientes para gerar o gráfico.")

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    arquivo = CHARTS_DIR / f"{_nome_arquivo_seguro(paciente.get('nome'))}_{paciente_id}_imc.png"

    plt.figure(figsize=(10, 5))
    plt.plot(datas, imcs, marker="o")
    plt.title(f"Evolução do IMC - {paciente.get('nome', '')}")
    plt.xlabel("Data")
    plt.ylabel("IMC")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(arquivo, dpi=150)
    plt.close()

    return str(arquivo)


def gerar_grafico_cintura(paciente_id: str) -> str:
    paciente = _validar_paciente(paciente_id)
    series = preparar_series_graficos_antropometria(paciente_id)

    datas = series.get("datas", [])
    cinturas = series.get("cinturas", [])

    if not datas or not any(v is not None for v in cinturas):
        raise ValueError("Não há dados de circunferência da cintura suficientes para gerar o gráfico.")

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    arquivo = CHARTS_DIR / f"{_nome_arquivo_seguro(paciente.get('nome'))}_{paciente_id}_cintura.png"

    plt.figure(figsize=(10, 5))
    plt.plot(datas, cinturas, marker="o")
    plt.title(f"Evolução da circunferência da cintura - {paciente.get('nome', '')}")
    plt.xlabel("Data")
    plt.ylabel("Cintura (cm)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(arquivo, dpi=150)
    plt.close()

    return str(arquivo)


def gerar_grafico_status_exames(paciente_id: str) -> str:
    paciente = _validar_paciente(paciente_id)
    executar_analise_exames()
    analises = listar_analises_por_paciente(paciente_id)

    if not analises:
        raise ValueError("Não há análises de exames para gerar o gráfico.")

    contagem = Counter(a.get("status", "Sem status") for a in analises)
    labels = list(contagem.keys())
    valores = list(contagem.values())

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    arquivo = CHARTS_DIR / f"{_nome_arquivo_seguro(paciente.get('nome'))}_{paciente_id}_status_exames.png"

    plt.figure(figsize=(9, 5))
    plt.bar(labels, valores)
    plt.title(f"Distribuição dos exames por status - {paciente.get('nome', '')}")
    plt.xlabel("Status")
    plt.ylabel("Quantidade")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(arquivo, dpi=150)
    plt.close()

    return str(arquivo)


def gerar_grafico_exames_alterados(paciente_id: str) -> str:
    paciente = _validar_paciente(paciente_id)
    executar_analise_exames()
    alterados = listar_exames_alterados_por_paciente(paciente_id)

    somente_alterados = [a for a in alterados if a.get("status") in ["Acima", "Abaixo"]]

    if not somente_alterados:
        raise ValueError("Não há exames acima ou abaixo da referência para gerar o gráfico.")

    contagem = Counter(a.get("nome_exame_padronizado", "Exame") for a in somente_alterados)
    labels = list(contagem.keys())
    valores = list(contagem.values())

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    arquivo = CHARTS_DIR / f"{_nome_arquivo_seguro(paciente.get('nome'))}_{paciente_id}_exames_alterados.png"

    plt.figure(figsize=(10, 5))
    plt.bar(labels, valores)
    plt.title(f"Exames alterados por tipo - {paciente.get('nome', '')}")
    plt.xlabel("Exame")
    plt.ylabel("Ocorrências")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(arquivo, dpi=150)
    plt.close()

    return str(arquivo)


def gerar_todos_graficos_paciente(paciente_id: str) -> dict:
    resultados = {}

    funcoes = {
        "peso": gerar_grafico_peso,
        "imc": gerar_grafico_imc,
        "cintura": gerar_grafico_cintura,
        "status_exames": gerar_grafico_status_exames,
        "exames_alterados": gerar_grafico_exames_alterados,
    }

    for nome, funcao in funcoes.items():
        try:
            resultados[nome] = {
                "sucesso": True,
                "arquivo": funcao(paciente_id),
                "erro": "",
            }
        except Exception as exc:
            resultados[nome] = {
                "sucesso": False,
                "arquivo": "",
                "erro": str(exc),
            }

    return resultados

from collections import Counter, defaultdict
from typing import Any

from src.exames import listar_analises_por_paciente, listar_exames_alterados_por_paciente


PAINEIS_EXAMES = {
    "Glicêmico / Metabólico": [
        "glicose",
        "glicemia",
        "hemoglobina glicada",
        "hba1c",
        "insulina",
        "homa",
    ],
    "Lipídico / Cardiovascular": [
        "colesterol",
        "hdl",
        "ldl",
        "vldl",
        "triglicer",
        "triglicerídeos",
    ],
    "Vitaminas / Minerais": [
        "vitamina d",
        "vit d",
        "b12",
        "ácido fólico",
        "folato",
        "ferro",
        "ferritina",
        "zinco",
        "magnésio",
    ],
    "Hepático": [
        "tgo",
        "ast",
        "tgp",
        "alt",
        "gama",
        "gt",
        "bilirrubina",
        "fosfatase alcalina",
    ],
    "Renal": [
        "creatinina",
        "ureia",
        "ácido úrico",
        "microalbuminúria",
        "albuminúria",
    ],
    "Hematológico": [
        "hemoglobina",
        "hematócrito",
        "hemácias",
        "leucócitos",
        "plaquetas",
        "hemograma",
    ],
    "Inflamatório / Imunológico": [
        "pcr",
        "proteína c",
        "vhs",
    ],
    "Tireoidiano": [
        "tsh",
        "t3",
        "t4",
        "t4 livre",
    ],
}


def classificar_painel(nome_exame: str) -> str:
    nome = (nome_exame or "").lower()
    for painel, termos in PAINEIS_EXAMES.items():
        for termo in termos:
            if termo in nome:
                return painel
    return "Outros"


def _to_float(valor: Any):
    try:
        if valor is None:
            return None
        valor = str(valor).replace(",", ".").strip()
        if not valor:
            return None
        return float(valor)
    except Exception:
        return None


def gerar_insights_exames_paciente(paciente_id: str) -> dict:
    analises = listar_analises_por_paciente(paciente_id)
    alterados = listar_exames_alterados_por_paciente(paciente_id)

    total = len(analises)
    cont_status = Counter([a.get("status", "Indefinido") for a in analises])

    por_painel = defaultdict(lambda: {
        "total": 0,
        "normal": 0,
        "alterados": 0,
        "sem_referencia": 0,
        "invalidos": 0,
        "exames": [],
    })

    alertas = []

    for item in analises:
        nome = item.get("nome_exame_padronizado") or item.get("nome_exame") or ""
        painel = classificar_painel(nome)
        status = item.get("status", "Indefinido")

        por_painel[painel]["total"] += 1
        por_painel[painel]["exames"].append(item)

        if status == "Normal":
            por_painel[painel]["normal"] += 1
        elif status in ["Acima", "Abaixo"]:
            por_painel[painel]["alterados"] += 1
        elif status == "Sem referência":
            por_painel[painel]["sem_referencia"] += 1
        elif status == "Resultado inválido":
            por_painel[painel]["invalidos"] += 1

    for item in alterados:
        nome = item.get("nome_exame_padronizado") or item.get("nome_exame") or "Exame"
        status = item.get("status", "")
        resultado = item.get("resultado", "")
        unidade = item.get("unidade", "")
        valor_min = item.get("valor_min", "")
        valor_max = item.get("valor_max", "")

        if status in ["Acima", "Abaixo"]:
            alertas.append({
                "tipo": "Alterado",
                "painel": classificar_painel(nome),
                "mensagem": f"{nome}: resultado {resultado} {unidade} está {status.lower()} da referência cadastrada ({valor_min} a {valor_max} {unidade}).",
                "exame": nome,
                "status": status,
            })
        elif status == "Sem referência":
            alertas.append({
                "tipo": "Sem referência",
                "painel": classificar_painel(nome),
                "mensagem": f"{nome}: exame sem referência cadastrada para comparação.",
                "exame": nome,
                "status": status,
            })
        elif status == "Resultado inválido":
            alertas.append({
                "tipo": "Resultado inválido",
                "painel": classificar_painel(nome),
                "mensagem": f"{nome}: resultado não pôde ser interpretado numericamente.",
                "exame": nome,
                "status": status,
            })

    prioridades = []
    for painel, dados in por_painel.items():
        score = dados["alterados"] * 3 + dados["sem_referencia"] + dados["invalidos"] * 2
        if score > 0:
            prioridades.append({
                "painel": painel,
                "score": score,
                "alterados": dados["alterados"],
                "sem_referencia": dados["sem_referencia"],
                "invalidos": dados["invalidos"],
                "total": dados["total"],
            })

    prioridades = sorted(prioridades, key=lambda x: x["score"], reverse=True)

    if not analises:
        resumo_executivo = "Nenhuma análise de exame disponível para este paciente."
    elif not alertas:
        resumo_executivo = "Todos os exames analisados estão dentro das referências cadastradas."
    else:
        painel_top = prioridades[0]["painel"] if prioridades else "Exames"
        resumo_executivo = (
            f"Foram analisados {total} exames. "
            f"Há {cont_status.get('Acima', 0) + cont_status.get('Abaixo', 0)} exames fora da referência cadastrada, "
            f"{cont_status.get('Sem referência', 0)} sem referência e "
            f"{cont_status.get('Resultado inválido', 0)} com resultado inválido. "
            f"Principal painel de atenção: {painel_top}."
        )

    recomendacoes = []
    if cont_status.get("Sem referência", 0) > 0:
        recomendacoes.append("Cadastrar ou revisar referências para exames sem parâmetro comparativo.")
    if cont_status.get("Resultado inválido", 0) > 0:
        recomendacoes.append("Revisar digitação dos resultados e unidades dos exames inválidos.")
    if cont_status.get("Acima", 0) + cont_status.get("Abaixo", 0) > 0:
        recomendacoes.append("Avaliar exames alterados em conjunto com anamnese, antropometria, sintomas e contexto clínico.")
    if not recomendacoes and total > 0:
        recomendacoes.append("Manter acompanhamento evolutivo e comparar exames futuros com os registros anteriores.")

    return {
        "total": total,
        "status": dict(cont_status),
        "por_painel": dict(por_painel),
        "alertas": alertas,
        "prioridades": prioridades,
        "resumo_executivo": resumo_executivo,
        "recomendacoes": recomendacoes,
    }

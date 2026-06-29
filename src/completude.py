from src.pacientes import buscar_paciente_por_id
from src.anamnese import listar_anamneses_por_paciente, listar_recordatorios_por_paciente
from src.antropometria import listar_antropometrias_por_paciente
from src.exames import listar_exames_por_paciente, listar_analises_por_paciente


CAMPOS_PACIENTE = [
    "nome",
    "data_nascimento",
    "idade",
    "sexo",
    "telefone",
    "email",
    "profissao",
]

CAMPOS_ANAMNESE = [
    "queixa_principal",
    "sintomas",
    "historia_patologica_pregressa",
    "historia_familiar",
    "atividade_fisica",
    "consumo_alcool",
    "tabagismo",
    "qualidade_sono",
    "funcionamento_intestinal",
    "funcionamento_urinario",
    "ingestao_agua_dia",
    "alimentos_preferidos",
    "habitos_fim_de_semana",
]

CAMPOS_ANTROPOMETRIA = [
    "peso",
    "altura",
    "imc",
    "circunferencia_cintura",
]

PESOS = {
    "cadastro": 25,
    "anamnese": 35,
    "antropometria": 20,
    "exames": 15,
    "analise": 5,
}


def _preenchido(valor) -> bool:
    if valor is None:
        return False
    texto = str(valor).strip()
    return texto not in ["", "None", "nan", "NaN"]


def _percentual_campos(registro: dict, campos: list[str]) -> tuple[int, int, float]:
    if not registro:
        return 0, len(campos), 0.0

    preenchidos = sum(1 for campo in campos if _preenchido(registro.get(campo)))
    total = len(campos)
    percentual = (preenchidos / total * 100) if total else 0
    return preenchidos, total, percentual


def _mais_recente(lista: list[dict], campo_data: str) -> dict:
    if not lista:
        return {}
    return sorted(lista, key=lambda x: x.get(campo_data, ""), reverse=True)[0]


def calcular_completude_paciente(paciente_id: str) -> dict:
    paciente = buscar_paciente_por_id(paciente_id)
    anamneses = listar_anamneses_por_paciente(paciente_id)
    recordatorios = listar_recordatorios_por_paciente(paciente_id)
    antropometrias = listar_antropometrias_por_paciente(paciente_id)
    exames = listar_exames_por_paciente(paciente_id)
    analises = listar_analises_por_paciente(paciente_id)

    anamnese = _mais_recente(anamneses, "data_anamnese")
    antrop = _mais_recente(antropometrias, "data_avaliacao")

    cad_ok, cad_total, cad_pct = _percentual_campos(paciente or {}, CAMPOS_PACIENTE)
    ana_ok, ana_total, ana_pct = _percentual_campos(anamnese, CAMPOS_ANAMNESE)
    ant_ok, ant_total, ant_pct = _percentual_campos(antrop, CAMPOS_ANTROPOMETRIA)

    exames_pct = 100 if len(exames) >= 3 else (len(exames) / 3 * 100 if exames else 0)
    analise_pct = 100 if analises else 0
    recordatorio_pct = 100 if recordatorios else 0

    # Recordatório entra como bônus dentro do bloco de anamnese, sem estourar 100%.
    ana_pct_com_bonus = min(100, ana_pct * 0.85 + recordatorio_pct * 0.15)

    percentual_geral = (
        cad_pct * PESOS["cadastro"] / 100
        + ana_pct_com_bonus * PESOS["anamnese"] / 100
        + ant_pct * PESOS["antropometria"] / 100
        + exames_pct * PESOS["exames"] / 100
        + analise_pct * PESOS["analise"] / 100
    )

    percentual_geral = round(percentual_geral, 1)

    pendencias = []
    if cad_pct < 80:
        pendencias.append("Completar dados cadastrais essenciais.")
    if ana_pct < 75:
        pendencias.append("Completar anamnese guiada.")
    if not recordatorios:
        pendencias.append("Cadastrar recordatório alimentar.")
    if ant_pct < 75:
        pendencias.append("Cadastrar avaliação antropométrica completa.")
    if len(exames) < 3:
        pendencias.append("Cadastrar exames laboratoriais.")
    if exames and not analises:
        pendencias.append("Executar análise comparativa dos exames.")

    if percentual_geral >= 85:
        nivel = "Completo"
        cor = "green"
        descricao = "Cadastro adequado para análise e acompanhamento."
    elif percentual_geral >= 65:
        nivel = "Aceitável"
        cor = "orange"
        descricao = "Cadastro utilizável, mas ainda com pontos importantes a completar."
    else:
        nivel = "Incompleto"
        cor = "red"
        descricao = "Cadastro ainda insuficiente para uma análise consistente."

    return {
        "paciente_id": paciente_id,
        "percentual": percentual_geral,
        "nivel": nivel,
        "cor": cor,
        "descricao": descricao,
        "pendencias": pendencias,
        "blocos": {
            "Cadastro": {
                "percentual": round(cad_pct, 1),
                "preenchidos": cad_ok,
                "total": cad_total,
                "peso": PESOS["cadastro"],
            },
            "Anamnese": {
                "percentual": round(ana_pct_com_bonus, 1),
                "preenchidos": ana_ok,
                "total": ana_total,
                "peso": PESOS["anamnese"],
            },
            "Antropometria": {
                "percentual": round(ant_pct, 1),
                "preenchidos": ant_ok,
                "total": ant_total,
                "peso": PESOS["antropometria"],
            },
            "Exames": {
                "percentual": round(exames_pct, 1),
                "preenchidos": min(len(exames), 3),
                "total": 3,
                "peso": PESOS["exames"],
            },
            "Análise": {
                "percentual": round(analise_pct, 1),
                "preenchidos": 1 if analises else 0,
                "total": 1,
                "peso": PESOS["analise"],
            },
        },
    }


def listar_completude_pacientes() -> list[dict]:
    from src.pacientes import listar_pacientes

    linhas = []
    for paciente in listar_pacientes():
        paciente_id = paciente.get("paciente_id", "")
        c = calcular_completude_paciente(paciente_id)
        linhas.append({
            "paciente_id": paciente_id,
            "nome": paciente.get("nome", ""),
            "percentual": c["percentual"],
            "nivel": c["nivel"],
            "pendencias": len(c["pendencias"]),
        })

    return sorted(linhas, key=lambda x: x["percentual"])

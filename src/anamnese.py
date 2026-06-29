from .database import adicionar_linha, ler_csv, obter_proximo_id, atualizar_linha, remover_linha
from .pacientes import buscar_paciente_por_id
from .utils import data_hoje, normalizar_texto, texto_sim_nao


def validar_anamnese(dados: dict) -> list[str]:
    paciente_id = str(dados.get("paciente_id", "")).strip()
    if not paciente_id:
        return ["O campo 'paciente_id' é obrigatório."]
    if not buscar_paciente_por_id(paciente_id):
        return [f"Paciente ID {paciente_id} não encontrado."]
    return []


def cadastrar_anamnese(dados: dict) -> dict:
    erros = validar_anamnese(dados)
    if erros:
        return {"sucesso": False, "erros": erros, "anamnese": None}

    campos = [
        "queixa_principal", "historia_doenca_atual", "sintomas", "historia_patologica_pregressa",
        "historia_familiar", "numero_filhos_idades", "atividade_fisica", "horario_atividade_fisica",
        "consumo_alcool", "tabagismo", "qualidade_sono", "hora_acordar", "hora_dormir",
        "comportamento_peso", "disposicao_fisica", "funcionamento_intestinal", "funcionamento_urinario",
        "internacoes_cirurgias", "medicamentos_suplementos", "intolerancia_alergia_alimentar",
        "denticao", "mastigacao", "quem_cozinha", "apetite", "horario_mais_fome", "ingestao_agua_dia",
        "qual_tratamento", "alimentos_preferidos", "alimentos_que_nao_gosta", "habitos_fim_de_semana"
    ]

    anamnese = {
        "anamnese_id": obter_proximo_id("anamnese", "anamnese_id"),
        "paciente_id": str(dados.get("paciente_id", "")).strip(),
        "data_anamnese": dados.get("data_anamnese") or data_hoje(),
        "amamentou": texto_sim_nao(dados.get("amamentou", "")),
        "tratamento_nutricional_anterior": texto_sim_nao(dados.get("tratamento_nutricional_anterior", "")),
        "habito_beliscar": texto_sim_nao(dados.get("habito_beliscar", "")),
    }

    for campo in campos:
        anamnese[campo] = dados.get(campo, "")

    adicionar_linha("anamnese", anamnese)
    return {"sucesso": True, "erros": [], "anamnese": anamnese}


def cadastrar_recordatorio(dados: dict) -> dict:
    paciente_id = str(dados.get("paciente_id", "")).strip()
    if not paciente_id:
        return {"sucesso": False, "erros": ["O campo 'paciente_id' é obrigatório."], "recordatorio": None}
    if not buscar_paciente_por_id(paciente_id):
        return {"sucesso": False, "erros": [f"Paciente ID {paciente_id} não encontrado."], "recordatorio": None}

    recordatorio = {
        "recordatorio_id": obter_proximo_id("recordatorio_habitual", "recordatorio_id"),
        "paciente_id": paciente_id,
        "data_registro": dados.get("data_registro") or data_hoje(),
        "desjejum": dados.get("desjejum", ""),
        "lanche_manha": dados.get("lanche_manha", ""),
        "almoco": dados.get("almoco", ""),
        "lanche_tarde": dados.get("lanche_tarde", ""),
        "jantar": dados.get("jantar", ""),
        "ceia": dados.get("ceia", ""),
        "observacoes": dados.get("observacoes", ""),
    }

    adicionar_linha("recordatorio_habitual", recordatorio)
    return {"sucesso": True, "erros": [], "recordatorio": recordatorio}


def listar_anamneses_por_paciente(paciente_id: str) -> list[dict]:
    return sorted([a for a in ler_csv("anamnese") if str(a.get("paciente_id", "")).strip() == str(paciente_id).strip()], key=lambda a: a.get("data_anamnese", ""), reverse=True)


def listar_recordatorios_por_paciente(paciente_id: str) -> list[dict]:
    return sorted([r for r in ler_csv("recordatorio_habitual") if str(r.get("paciente_id", "")).strip() == str(paciente_id).strip()], key=lambda r: r.get("data_registro", ""), reverse=True)


def obter_anamnese_mais_recente(paciente_id: str) -> dict | None:
    anamneses = listar_anamneses_por_paciente(paciente_id)
    return anamneses[0] if anamneses else None


def obter_recordatorio_mais_recente(paciente_id: str) -> dict | None:
    recordatorios = listar_recordatorios_por_paciente(paciente_id)
    return recordatorios[0] if recordatorios else None


def atualizar_anamnese(anamnese_id: str, novos_dados: dict) -> bool:
    return atualizar_linha("anamnese", "anamnese_id", anamnese_id, novos_dados)


def excluir_anamnese(anamnese_id: str) -> bool:
    return remover_linha("anamnese", "anamnese_id", anamnese_id)


def formatar_anamnese_resumo(anamnese: dict) -> str:
    return f"Anamnese {anamnese.get('anamnese_id', '')} | Paciente {anamnese.get('paciente_id', '')} | Data {anamnese.get('data_anamnese', '')} | Queixa: {anamnese.get('queixa_principal', '')[:60]}"


def gerar_resumo_nutricional_paciente(paciente_id: str) -> dict:
    anamnese = obter_anamnese_mais_recente(paciente_id)
    recordatorio = obter_recordatorio_mais_recente(paciente_id)

    if not anamnese:
        return {"paciente_id": paciente_id, "possui_anamnese": False, "resumo": "Paciente ainda não possui anamnese cadastrada."}

    pontos_atencao = []
    if normalizar_texto(anamnese.get("habito_beliscar", "")) == "sim":
        pontos_atencao.append("Relata hábito de beliscar.")
    if anamnese.get("ingestao_agua_dia"):
        pontos_atencao.append(f"Ingestão de água/dia: {anamnese.get('ingestao_agua_dia')}.")
    if anamnese.get("qualidade_sono"):
        pontos_atencao.append(f"Qualidade do sono: {anamnese.get('qualidade_sono')}.")
    if anamnese.get("atividade_fisica"):
        pontos_atencao.append(f"Atividade física: {anamnese.get('atividade_fisica')}.")
    if recordatorio:
        pontos_atencao.append("Recordatório habitual cadastrado.")

    return {
        "paciente_id": paciente_id,
        "possui_anamnese": True,
        "data_anamnese": anamnese.get("data_anamnese", ""),
        "queixa_principal": anamnese.get("queixa_principal", ""),
        "pontos_atencao": pontos_atencao,
        "resumo": " | ".join(pontos_atencao) if pontos_atencao else "Anamnese cadastrada sem pontos de atenção automáticos."
    }

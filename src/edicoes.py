import json

from src.database import adicionar_linha, ler_csv, atualizar_linha, obter_proximo_id, HEADERS
from src.utils import data_hora_atual
from src.analises import executar_analise_exames


BASES_EDITAVEIS = {
    "pacientes": "paciente_id",
    "anamnese": "anamnese_id",
    "recordatorio_habitual": "recordatorio_id",
    "antropometria": "antropometria_id",
    "exames": "exame_id",
    "referencias_exames": "referencia_id",
    "alias_exames": "alias",
    "evolucao_conduta": "evolucao_id",
}


def campo_id_base(nome_base: str) -> str:
    return BASES_EDITAVEIS[nome_base]


def listar_registros(nome_base: str) -> list[dict]:
    return ler_csv(nome_base)


def buscar_registro(nome_base: str, registro_id: str) -> dict | None:
    campo_id = campo_id_base(nome_base)
    for r in ler_csv(nome_base):
        if str(r.get(campo_id, "")).strip() == str(registro_id).strip():
            return r
    return None


def registrar_historico_edicao(nome_base: str, registro_id: str, campo: str, valor_anterior: str, valor_novo: str, usuario: str, motivo: str):
    adicionar_linha("historico_edicoes", {
        "historico_id": obter_proximo_id("historico_edicoes", "historico_id"),
        "data_hora": data_hora_atual(),
        "base": nome_base,
        "registro_id": registro_id,
        "campo": campo,
        "valor_anterior": valor_anterior,
        "valor_novo": valor_novo,
        "usuario": usuario,
        "motivo": motivo,
    })


def atualizar_registro_com_historico(nome_base: str, registro_id: str, novos_dados: dict, usuario: str = "sistema", motivo: str = "") -> dict:
    if nome_base not in BASES_EDITAVEIS:
        return {"sucesso": False, "erro": "Base não editável.", "alteracoes": 0}

    atual = buscar_registro(nome_base, registro_id)
    if not atual:
        return {"sucesso": False, "erro": "Registro não encontrado.", "alteracoes": 0}

    campo_id = campo_id_base(nome_base)
    alteracoes = 0
    dados_para_atualizar = {}

    for campo, valor_novo in novos_dados.items():
        if campo == campo_id:
            continue
        valor_anterior = str(atual.get(campo, ""))
        valor_novo = str(valor_novo)
        if valor_anterior != valor_novo:
            registrar_historico_edicao(nome_base, registro_id, campo, valor_anterior, valor_novo, usuario, motivo)
            dados_para_atualizar[campo] = valor_novo
            alteracoes += 1

    if not dados_para_atualizar:
        return {"sucesso": True, "erro": "", "alteracoes": 0}

    ok = atualizar_linha(nome_base, campo_id, registro_id, dados_para_atualizar)

    if ok and nome_base in ["exames", "referencias_exames", "alias_exames"]:
        executar_analise_exames()

    return {"sucesso": ok, "erro": "" if ok else "Falha ao atualizar.", "alteracoes": alteracoes}


def historico_por_base_registro(nome_base: str, registro_id: str) -> list[dict]:
    return [
        h for h in ler_csv("historico_edicoes")
        if h.get("base") == nome_base and str(h.get("registro_id", "")) == str(registro_id)
    ]


def campos_editaveis(nome_base: str) -> list[str]:
    campo_id = campo_id_base(nome_base)
    return [c for c in HEADERS[nome_base] if c != campo_id]

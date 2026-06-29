from src.catalogo_exames import EXAMES_COMUNS, aliases_para_cadastro
from src.exames import listar_exames_por_paciente
from src.utils import data_atual, normalizar_texto
from src.analises import carregar_alias


def _data_normalizada(data_exame: str) -> str:
    return str(data_exame or data_atual()).strip()


def _mapa_alias_total() -> dict:
    mapa = {}

    # Aliases cadastrados no banco.
    try:
        mapa.update(carregar_alias())
    except Exception:
        pass

    # Aliases do catálogo, mesmo que o usuário ainda não tenha carregado manualmente.
    for item in aliases_para_cadastro():
        alias = normalizar_texto(item.get("alias", ""))
        nome = str(item.get("nome_padronizado", "")).strip()
        if alias and nome:
            mapa[alias] = nome

    return mapa


def nome_canonico_exame(nome_exame: str) -> str:
    nome = str(nome_exame or "").strip()
    if not nome:
        return ""

    mapa = _mapa_alias_total()
    chave = normalizar_texto(nome)

    return mapa.get(chave, nome)


def exames_ja_cadastrados_na_data(paciente_id: str, data_exame: str) -> set[str]:
    data = _data_normalizada(data_exame)
    exames = listar_exames_por_paciente(paciente_id)

    cadastrados = set()
    for exame in exames:
        if str(exame.get("data_exame", "")).strip() == data:
            nome = nome_canonico_exame(exame.get("nome_exame", ""))
            if nome:
                cadastrados.add(normalizar_texto(nome))

    return cadastrados


def exames_disponiveis_para_data(paciente_id: str, data_exame: str) -> list[str]:
    cadastrados_norm = exames_ja_cadastrados_na_data(paciente_id, data_exame)
    disponiveis = []

    for exame in EXAMES_COMUNS:
        if exame in ["", "Outro"]:
            disponiveis.append(exame)
            continue

        canonico = nome_canonico_exame(exame)
        if normalizar_texto(canonico) not in cadastrados_norm:
            disponiveis.append(exame)

    return disponiveis


def validar_exame_duplicado(paciente_id: str, data_exame: str, nome_exame: str) -> dict:
    data = _data_normalizada(data_exame)
    nome = str(nome_exame or "").strip()

    if not nome:
        return {"duplicado": False, "mensagem": ""}

    cadastrados_norm = exames_ja_cadastrados_na_data(paciente_id, data)
    canonico = nome_canonico_exame(nome)
    canonico_norm = normalizar_texto(canonico)

    if canonico_norm in cadastrados_norm:
        return {
            "duplicado": True,
            "mensagem": f"O exame '{canonico}' já foi cadastrado para este paciente na data {data}.",
        }

    return {"duplicado": False, "mensagem": ""}

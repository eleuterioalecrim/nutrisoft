from .database import adicionar_linha, ler_csv, obter_proximo_id, atualizar_linha, remover_linha
from .pacientes import buscar_paciente_por_id
from .utils import converter_float, data_hoje, normalizar_texto, formatar_numero
from .analises import executar_analise_exames, carregar_alias, padronizar_nome_exame


def validar_exame(dados: dict) -> list[str]:
    erros = []
    paciente_id = str(dados.get("paciente_id", "")).strip()
    if not paciente_id:
        erros.append("O campo 'paciente_id' é obrigatório.")
    elif not buscar_paciente_por_id(paciente_id):
        erros.append(f"Paciente ID {paciente_id} não encontrado.")

    if not str(dados.get("nome_exame", "")).strip():
        erros.append("O campo 'nome_exame' é obrigatório.")
    if converter_float(dados.get("resultado")) is None:
        erros.append("O campo 'resultado' deve ser numérico.")
    if not str(dados.get("unidade", "")).strip():
        erros.append("O campo 'unidade' é obrigatório.")
    return erros


def cadastrar_exame(dados: dict, executar_analise: bool = True) -> dict:
    erros = validar_exame(dados)
    if erros:
        return {"sucesso": False, "erros": erros, "exame": None}

    exame = {
        "exame_id": obter_proximo_id("exames", "exame_id"),
        "paciente_id": str(dados.get("paciente_id", "")).strip(),
        "data_exame": dados.get("data_exame") or data_hoje(),
        "nome_exame": str(dados.get("nome_exame", "")).strip(),
        "resultado": str(dados.get("resultado", "")).replace(",", "."),
        "unidade": str(dados.get("unidade", "")).strip(),
        "observacoes": dados.get("observacoes", ""),
    }

    adicionar_linha("exames", exame)
    if executar_analise:
        executar_analise_exames()
    return {"sucesso": True, "erros": [], "exame": exame}


def listar_exames_por_paciente(paciente_id: str) -> list[dict]:
    return sorted([e for e in ler_csv("exames") if str(e.get("paciente_id", "")).strip() == str(paciente_id).strip()], key=lambda e: e.get("data_exame", ""), reverse=True)


def listar_exames_por_nome(nome_exame: str) -> list[dict]:
    termo = normalizar_texto(nome_exame)
    return sorted([e for e in ler_csv("exames") if termo in normalizar_texto(e.get("nome_exame", ""))], key=lambda e: e.get("data_exame", ""), reverse=True)


def buscar_exame_por_id(exame_id: str) -> dict | None:
    for exame in ler_csv("exames"):
        if str(exame.get("exame_id", "")).strip() == str(exame_id).strip():
            return exame
    return None


def atualizar_exame(exame_id: str, novos_dados: dict) -> bool:
    if "resultado" in novos_dados:
        novos_dados["resultado"] = str(novos_dados["resultado"]).replace(",", ".")
    atualizado = atualizar_linha("exames", "exame_id", exame_id, novos_dados)
    if atualizado:
        executar_analise_exames()
    return atualizado


def excluir_exame(exame_id: str) -> bool:
    excluido = remover_linha("exames", "exame_id", exame_id)
    if excluido:
        executar_analise_exames()
    return excluido


def validar_referencia(dados: dict) -> list[str]:
    erros = []
    if not str(dados.get("nome_exame", "")).strip():
        erros.append("O campo 'nome_exame' é obrigatório.")

    sexo = str(dados.get("sexo", "Todos")).strip() or "Todos"
    if sexo not in ["Todos", "M", "F", "Outro", "Não informado"]:
        erros.append("O campo 'sexo' deve ser Todos, M, F, Outro ou Não informado.")

    for campo in ["idade_min", "idade_max", "valor_min", "valor_max"]:
        if converter_float(dados.get(campo)) is None:
            erros.append(f"O campo '{campo}' deve ser numérico.")

    if not str(dados.get("unidade", "")).strip():
        erros.append("O campo 'unidade' é obrigatório.")
    return erros


def cadastrar_referencia_exame(dados: dict, executar_analise: bool = True) -> dict:
    erros = validar_referencia(dados)
    if erros:
        return {"sucesso": False, "erros": erros, "referencia": None}

    referencia = {
        "referencia_id": obter_proximo_id("referencias_exames", "referencia_id"),
        "nome_exame": str(dados.get("nome_exame", "")).strip(),
        "sexo": str(dados.get("sexo", "Todos")).strip() or "Todos",
        "idade_min": str(dados.get("idade_min", "")).replace(",", "."),
        "idade_max": str(dados.get("idade_max", "")).replace(",", "."),
        "valor_min": str(dados.get("valor_min", "")).replace(",", "."),
        "valor_max": str(dados.get("valor_max", "")).replace(",", "."),
        "unidade": str(dados.get("unidade", "")).strip(),
        "fonte_referencia": dados.get("fonte_referencia", ""),
        "observacoes": dados.get("observacoes", ""),
    }

    adicionar_linha("referencias_exames", referencia)
    if executar_analise:
        executar_analise_exames()
    return {"sucesso": True, "erros": [], "referencia": referencia}


def listar_referencias_exames() -> list[dict]:
    return sorted(ler_csv("referencias_exames"), key=lambda r: (normalizar_texto(r.get("nome_exame", "")), r.get("sexo", "")))


def cadastrar_alias_exame(alias: str, nome_padronizado: str) -> dict:
    alias = str(alias or "").strip()
    nome_padronizado = str(nome_padronizado or "").strip()
    if not alias or not nome_padronizado:
        return {"sucesso": False, "erros": ["Alias e nome padronizado são obrigatórios."], "alias": None}

    registro = {"alias": normalizar_texto(alias), "nome_padronizado": nome_padronizado}
    adicionar_linha("alias_exames", registro)
    executar_analise_exames()
    return {"sucesso": True, "erros": [], "alias": registro}


def listar_alias_exames() -> list[dict]:
    return sorted(ler_csv("alias_exames"), key=lambda a: normalizar_texto(a.get("alias", "")))


def listar_analises_por_paciente(paciente_id: str) -> list[dict]:
    return sorted([a for a in ler_csv("analise_exames") if str(a.get("paciente_id", "")).strip() == str(paciente_id).strip()], key=lambda a: a.get("data_exame", ""), reverse=True)


def listar_exames_alterados_por_paciente(paciente_id: str) -> list[dict]:
    return [a for a in listar_analises_por_paciente(paciente_id) if a.get("status") in ["Abaixo", "Acima", "Resultado inválido", "Sem referência"]]


def gerar_resumo_exames_paciente(paciente_id: str) -> dict:
    executar_analise_exames()
    analises = listar_analises_por_paciente(paciente_id)
    if not analises:
        return {"paciente_id": paciente_id, "possui_exames": False, "resumo": "Paciente ainda não possui exames cadastrados."}

    total = len(analises)
    normais = len([a for a in analises if a.get("status") == "Normal"])
    acima = len([a for a in analises if a.get("status") == "Acima"])
    abaixo = len([a for a in analises if a.get("status") == "Abaixo"])
    sem_ref = len([a for a in analises if a.get("status") == "Sem referência"])
    invalidos = len([a for a in analises if a.get("status") == "Resultado inválido"])
    alterados = [a for a in analises if a.get("status") in ["Acima", "Abaixo"]]

    return {
        "paciente_id": paciente_id,
        "possui_exames": True,
        "total": total,
        "normais": normais,
        "acima": acima,
        "abaixo": abaixo,
        "sem_referencia": sem_ref,
        "invalidos": invalidos,
        "principais_alertas": [f"{a.get('nome_exame_padronizado')} {a.get('status').lower()} da referência cadastrada." for a in alterados[:5]],
        "resumo": f"Total: {total} | Normais: {normais} | Acima: {acima} | Abaixo: {abaixo} | Sem referência: {sem_ref} | Inválidos: {invalidos}",
    }


def formatar_exame_resumo(exame: dict) -> str:
    mapa_alias = carregar_alias()
    nome_padronizado = padronizar_nome_exame(exame.get("nome_exame", ""), mapa_alias)
    return f"Exame {exame.get('exame_id', '')} | Data {exame.get('data_exame', '')} | {nome_padronizado} | Resultado {formatar_numero(exame.get('resultado'))} {exame.get('unidade', '')}"


def formatar_referencia_resumo(ref: dict) -> str:
    return f"Ref {ref.get('referencia_id', '')} | {ref.get('nome_exame', '')} | Sexo {ref.get('sexo', '')} | Idade {ref.get('idade_min', '')}-{ref.get('idade_max', '')} | {ref.get('valor_min', '')} a {ref.get('valor_max', '')} {ref.get('unidade', '')}"


def formatar_analise_resumo(analise: dict) -> str:
    return f"{analise.get('data_exame', '')} | {analise.get('nome_exame_padronizado', '')} | {analise.get('resultado', '')} {analise.get('unidade', '')} | Ref. {analise.get('valor_min', '')}-{analise.get('valor_max', '')} | Status: {analise.get('status', '')} | {analise.get('insight', '')}"

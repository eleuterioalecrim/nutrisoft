from .database import adicionar_linha, ler_csv, obter_proximo_id, atualizar_linha, remover_linha
from .utils import normalizar_texto, data_hoje, calcular_idade


def validar_paciente(dados: dict) -> list[str]:
    erros = []
    if not str(dados.get("nome", "")).strip():
        erros.append("O campo 'nome' é obrigatório.")

    sexo = str(dados.get("sexo", "")).strip()
    if sexo and sexo not in ["M", "F", "Outro", "Não informado"]:
        erros.append("O campo 'sexo' deve ser M, F, Outro ou Não informado.")

    return erros


def cadastrar_paciente(dados: dict) -> dict:
    erros = validar_paciente(dados)
    if erros:
        return {"sucesso": False, "erros": erros, "paciente": None}

    data_nascimento = str(dados.get("data_nascimento", "")).strip()
    idade = dados.get("idade", "")

    if not idade and data_nascimento:
        idade_calculada = calcular_idade(data_nascimento)
        idade = idade_calculada if idade_calculada is not None else ""

    paciente = {
        "paciente_id": obter_proximo_id("pacientes", "paciente_id"),
        "data_cadastro": dados.get("data_cadastro") or data_hoje(),
        "nome": str(dados.get("nome", "")).strip(),
        "data_nascimento": data_nascimento,
        "idade": idade,
        "sexo": dados.get("sexo", "Não informado") or "Não informado",
        "telefone": dados.get("telefone", ""),
        "email": dados.get("email", ""),
        "profissao": dados.get("profissao", ""),
        "horario_trabalho": dados.get("horario_trabalho", ""),
        "observacoes": dados.get("observacoes", ""),
    }

    adicionar_linha("pacientes", paciente)
    return {"sucesso": True, "erros": [], "paciente": paciente}


def listar_pacientes() -> list[dict]:
    return sorted(ler_csv("pacientes"), key=lambda p: normalizar_texto(p.get("nome", "")))


def buscar_paciente_por_id(paciente_id: str) -> dict | None:
    for paciente in ler_csv("pacientes"):
        if str(paciente.get("paciente_id", "")).strip() == str(paciente_id).strip():
            return paciente
    return None


def buscar_pacientes_por_nome(nome: str) -> list[dict]:
    termo = normalizar_texto(nome)
    if not termo:
        return listar_pacientes()

    return sorted(
        [p for p in ler_csv("pacientes") if termo in normalizar_texto(p.get("nome", ""))],
        key=lambda p: normalizar_texto(p.get("nome", ""))
    )


def atualizar_paciente(paciente_id: str, novos_dados: dict) -> bool:
    if "data_nascimento" in novos_dados and "idade" not in novos_dados:
        idade = calcular_idade(novos_dados.get("data_nascimento", ""))
        if idade is not None:
            novos_dados["idade"] = idade
    return atualizar_linha("pacientes", "paciente_id", paciente_id, novos_dados)


def excluir_paciente(paciente_id: str) -> bool:
    return remover_linha("pacientes", "paciente_id", paciente_id)


def formatar_paciente_resumo(paciente: dict) -> str:
    return (
        f"{paciente.get('paciente_id', '')} | "
        f"{paciente.get('nome', '')} | "
        f"{paciente.get('idade', '')} anos | "
        f"{paciente.get('sexo', '')} | "
        f"{paciente.get('telefone', '')}"
    )

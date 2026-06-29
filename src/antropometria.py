from .database import adicionar_linha, ler_csv, obter_proximo_id, atualizar_linha, remover_linha
from .pacientes import buscar_paciente_por_id
from .utils import converter_float, data_hoje, formatar_numero


def calcular_imc(peso, altura) -> float | None:
    peso = converter_float(peso)
    altura = converter_float(altura)
    if peso is None or altura is None or altura <= 0:
        return None
    if altura > 3:
        altura = altura / 100
    return round(peso / (altura ** 2), 2)


def classificar_imc(imc) -> str:
    imc = converter_float(imc)
    if imc is None:
        return "IMC inválido"
    if imc < 18.5:
        return "Baixo peso"
    if imc < 25:
        return "Eutrofia"
    if imc < 30:
        return "Sobrepeso"
    if imc < 35:
        return "Obesidade grau I"
    if imc < 40:
        return "Obesidade grau II"
    return "Obesidade grau III"


def classificar_risco_cintura(circunferencia_cintura, sexo: str) -> str:
    cintura = converter_float(circunferencia_cintura)
    if cintura is None:
        return ""

    sexo = str(sexo or "").strip()

    if sexo == "M":
        if cintura >= 102:
            return "Risco aumentado"
        if cintura >= 94:
            return "Atenção"
        return "Sem risco aumentado pela cintura"

    if sexo == "F":
        if cintura >= 88:
            return "Risco aumentado"
        if cintura >= 80:
            return "Atenção"
        return "Sem risco aumentado pela cintura"

    return "Sem classificação por sexo não informado"


def validar_antropometria(dados: dict) -> list[str]:
    erros = []
    paciente_id = str(dados.get("paciente_id", "")).strip()
    if not paciente_id:
        erros.append("O campo 'paciente_id' é obrigatório.")
    elif not buscar_paciente_por_id(paciente_id):
        erros.append(f"Paciente ID {paciente_id} não encontrado.")

    peso = converter_float(dados.get("peso"))
    altura = converter_float(dados.get("altura"))

    if peso is None or peso <= 0:
        erros.append("O campo 'peso' deve ser numérico e maior que zero.")
    if altura is None or altura <= 0:
        erros.append("O campo 'altura' deve ser numérico e maior que zero.")

    return erros


def cadastrar_antropometria(dados: dict) -> dict:
    erros = validar_antropometria(dados)
    if erros:
        return {"sucesso": False, "erros": erros, "antropometria": None}

    paciente_id = str(dados.get("paciente_id", "")).strip()
    paciente = buscar_paciente_por_id(paciente_id)
    imc = calcular_imc(dados.get("peso"), dados.get("altura"))

    registro = {
        "antropometria_id": obter_proximo_id("antropometria", "antropometria_id"),
        "paciente_id": paciente_id,
        "data_avaliacao": dados.get("data_avaliacao") or data_hoje(),
        "peso": str(dados.get("peso", "")).replace(",", "."),
        "altura": str(dados.get("altura", "")).replace(",", "."),
        "imc": imc if imc is not None else "",
        "classificacao_imc": classificar_imc(imc),
        "circunferencia_cintura": str(dados.get("circunferencia_cintura", "")).replace(",", "."),
        "risco_cintura": classificar_risco_cintura(dados.get("circunferencia_cintura", ""), paciente.get("sexo", "") if paciente else ""),
        "observacoes": dados.get("observacoes", ""),
    }

    adicionar_linha("antropometria", registro)
    return {"sucesso": True, "erros": [], "antropometria": registro}


def listar_antropometrias_por_paciente(paciente_id: str) -> list[dict]:
    registros = [r for r in ler_csv("antropometria") if str(r.get("paciente_id", "")).strip() == str(paciente_id).strip()]
    return sorted(registros, key=lambda r: r.get("data_avaliacao", ""), reverse=True)


def obter_antropometria_mais_recente(paciente_id: str) -> dict | None:
    registros = listar_antropometrias_por_paciente(paciente_id)
    return registros[0] if registros else None


def buscar_antropometria_por_id(antropometria_id: str) -> dict | None:
    for registro in ler_csv("antropometria"):
        if str(registro.get("antropometria_id", "")).strip() == str(antropometria_id).strip():
            return registro
    return None


def atualizar_antropometria(antropometria_id: str, novos_dados: dict) -> bool:
    if "peso" in novos_dados or "altura" in novos_dados:
        atual = buscar_antropometria_por_id(antropometria_id)
        if atual:
            peso = novos_dados.get("peso", atual.get("peso"))
            altura = novos_dados.get("altura", atual.get("altura"))
            imc = calcular_imc(peso, altura)
            novos_dados["imc"] = imc if imc is not None else ""
            novos_dados["classificacao_imc"] = classificar_imc(imc)
    return atualizar_linha("antropometria", "antropometria_id", antropometria_id, novos_dados)


def excluir_antropometria(antropometria_id: str) -> bool:
    return remover_linha("antropometria", "antropometria_id", antropometria_id)


def calcular_evolucao_antropometrica(paciente_id: str) -> dict:
    registros = sorted(listar_antropometrias_por_paciente(paciente_id), key=lambda r: r.get("data_avaliacao", ""))
    if not registros:
        return {"paciente_id": paciente_id, "possui_dados": False, "resumo": "Paciente ainda não possui avaliação antropométrica cadastrada."}

    primeiro, ultimo = registros[0], registros[-1]
    peso_inicial = converter_float(primeiro.get("peso"))
    peso_atual = converter_float(ultimo.get("peso"))
    imc_inicial = converter_float(primeiro.get("imc"))
    imc_atual = converter_float(ultimo.get("imc"))
    cintura_inicial = converter_float(primeiro.get("circunferencia_cintura"))
    cintura_atual = converter_float(ultimo.get("circunferencia_cintura"))

    return {
        "paciente_id": paciente_id,
        "possui_dados": True,
        "primeira_data": primeiro.get("data_avaliacao", ""),
        "ultima_data": ultimo.get("data_avaliacao", ""),
        "peso_inicial": peso_inicial,
        "peso_atual": peso_atual,
        "delta_peso": None if peso_inicial is None or peso_atual is None else round(peso_atual - peso_inicial, 2),
        "imc_inicial": imc_inicial,
        "imc_atual": imc_atual,
        "delta_imc": None if imc_inicial is None or imc_atual is None else round(imc_atual - imc_inicial, 2),
        "cintura_inicial": cintura_inicial,
        "cintura_atual": cintura_atual,
        "delta_cintura": None if cintura_inicial is None or cintura_atual is None else round(cintura_atual - cintura_inicial, 2),
        "classificacao_atual": ultimo.get("classificacao_imc", ""),
        "risco_cintura_atual": ultimo.get("risco_cintura", ""),
    }


def preparar_series_graficos_antropometria(paciente_id: str) -> dict:
    registros = sorted(listar_antropometrias_por_paciente(paciente_id), key=lambda r: r.get("data_avaliacao", ""))
    return {
        "datas": [r.get("data_avaliacao", "") for r in registros],
        "pesos": [converter_float(r.get("peso")) for r in registros],
        "imcs": [converter_float(r.get("imc")) for r in registros],
        "cinturas": [converter_float(r.get("circunferencia_cintura")) for r in registros],
    }


def formatar_antropometria_resumo(registro: dict) -> str:
    return (
        f"Avaliação {registro.get('antropometria_id', '')} | "
        f"Data {registro.get('data_avaliacao', '')} | "
        f"Peso {formatar_numero(registro.get('peso'))} kg | "
        f"IMC {formatar_numero(registro.get('imc'))} | "
        f"{registro.get('classificacao_imc', '')} | "
        f"Cintura {formatar_numero(registro.get('circunferencia_cintura'))} cm"
    )

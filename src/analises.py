from .database import ler_csv, salvar_csv
from .utils import normalizar_texto, converter_float

def garantir_catalogo_referencias():
    """
    Garante que referências e aliases padrão estejam carregados antes da análise.

    Esta chamada é idempotente: cria o que falta e não duplica o que já existe.
    """
    try:
        from src.referencias_padrao import carregar_catalogo_padrao
        carregar_catalogo_padrao()
    except Exception:
        # A análise não deve quebrar a aplicação se o usuário estiver editando CSVs manualmente.
        pass



def carregar_alias() -> dict:
    mapa = {}

    # Aliases do CSV local
    for linha in ler_csv("alias_exames"):
        alias = normalizar_texto(linha.get("alias", ""))
        nome_padronizado = linha.get("nome_padronizado", "").strip()
        if alias and nome_padronizado:
            mapa[alias] = nome_padronizado

    # Aliases do catálogo central, mesmo que o CSV ainda não tenha sido carregado
    try:
        from src.catalogo_exames import aliases_para_cadastro
        for linha in aliases_para_cadastro():
            alias = normalizar_texto(linha.get("alias", ""))
            nome_padronizado = linha.get("nome_padronizado", "").strip()
            if alias and nome_padronizado:
                mapa[alias] = nome_padronizado
    except Exception:
        pass

    return mapa


def padronizar_nome_exame(nome_exame: str, mapa_alias: dict) -> str:
    chave = normalizar_texto(nome_exame)
    return mapa_alias.get(chave, str(nome_exame).strip())


def buscar_paciente(paciente_id: str, pacientes: list[dict]) -> dict | None:
    for paciente in pacientes:
        if str(paciente.get("paciente_id", "")).strip() == str(paciente_id).strip():
            return paciente
    return None


def buscar_referencia(nome_exame: str, paciente: dict | None, referencias: list[dict]) -> dict | None:
    sexo_paciente = "Todos"
    idade_paciente = None

    if paciente:
        sexo_paciente = str(paciente.get("sexo", "Todos")).strip() or "Todos"
        idade_paciente = converter_float(paciente.get("idade"))

    nome_norm = normalizar_texto(nome_exame)
    candidatas = []

    for ref in referencias:
        if normalizar_texto(ref.get("nome_exame", "")) != nome_norm:
            continue

        sexo_ref = str(ref.get("sexo", "Todos")).strip()
        if sexo_ref not in ["Todos", sexo_paciente]:
            continue

        idade_min = converter_float(ref.get("idade_min"))
        idade_max = converter_float(ref.get("idade_max"))

        if idade_paciente is not None and idade_min is not None and idade_max is not None:
            if not (idade_min <= idade_paciente <= idade_max):
                continue

        candidatas.append(ref)

    if not candidatas:
        return None

    candidatas.sort(key=lambda r: 0 if r.get("sexo") == sexo_paciente else 1)
    return candidatas[0]


def classificar_resultado(resultado, valor_min, valor_max) -> str:
    resultado = converter_float(resultado)
    valor_min = converter_float(valor_min)
    valor_max = converter_float(valor_max)

    if resultado is None:
        return "Resultado inválido"
    if valor_min is None or valor_max is None:
        return "Sem referência"
    if resultado < valor_min:
        return "Abaixo"
    if resultado > valor_max:
        return "Acima"
    return "Normal"


def gerar_insight(nome_exame: str, status: str) -> str:
    if status == "Abaixo":
        return f"{nome_exame} está abaixo da faixa de referência cadastrada."
    if status == "Acima":
        return f"{nome_exame} está acima da faixa de referência cadastrada."
    if status == "Normal":
        return f"{nome_exame} está dentro da faixa de referência cadastrada."
    if status == "Sem referência":
        return f"Não há referência cadastrada para {nome_exame}."
    if status == "Resultado inválido":
        return f"O resultado informado para {nome_exame} não pôde ser interpretado."
    return f"{nome_exame}: análise não classificada."


def executar_analise_exames() -> int:
    garantir_catalogo_referencias()
    pacientes = ler_csv("pacientes")
    exames = ler_csv("exames")
    referencias = ler_csv("referencias_exames")
    mapa_alias = carregar_alias()
    analises = []

    for idx, exame in enumerate(exames, start=1):
        paciente_id = exame.get("paciente_id", "")
        paciente = buscar_paciente(paciente_id, pacientes)
        nome_original = exame.get("nome_exame", "")
        nome_padronizado = padronizar_nome_exame(nome_original, mapa_alias)
        ref = buscar_referencia(nome_padronizado, paciente, referencias)

        if ref:
            valor_min = ref.get("valor_min", "")
            valor_max = ref.get("valor_max", "")
            fonte = ref.get("fonte_referencia", "")
        else:
            valor_min = ""
            valor_max = ""
            fonte = ""

        status = classificar_resultado(exame.get("resultado"), valor_min, valor_max)
        if not ref and status != "Resultado inválido":
            status = "Sem referência"

        analises.append({
            "analise_id": idx,
            "paciente_id": paciente_id,
            "data_exame": exame.get("data_exame", ""),
            "nome_exame_original": nome_original,
            "nome_exame_padronizado": nome_padronizado,
            "resultado": exame.get("resultado", ""),
            "unidade": exame.get("unidade", ""),
            "valor_min": valor_min,
            "valor_max": valor_max,
            "status": status,
            "insight": gerar_insight(nome_padronizado, status),
            "fonte_referencia": fonte,
        })

    salvar_csv("analise_exames", analises)
    return len(analises)

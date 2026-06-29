import unicodedata
from datetime import datetime, date


def normalizar_texto(texto: str) -> str:
    if texto is None:
        return ""

    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = " ".join(texto.split())
    return texto


def converter_float(valor):
    try:
        if valor is None or str(valor).strip() == "":
            return None
        return float(str(valor).replace(",", "."))
    except ValueError:
        return None


def formatar_numero(valor, casas=2) -> str:
    numero = converter_float(valor)
    if numero is None:
        return ""
    return f"{numero:.{casas}f}".replace(".", ",")


def data_hoje() -> str:
    return date.today().isoformat()


def calcular_idade(data_nascimento: str) -> int | None:
    if not data_nascimento:
        return None

    formatos = ["%Y-%m-%d", "%d/%m/%Y"]

    nascimento = None
    for formato in formatos:
        try:
            nascimento = datetime.strptime(data_nascimento, formato).date()
            break
        except ValueError:
            continue

    if nascimento is None:
        return None

    hoje = date.today()
    idade = hoje.year - nascimento.year - (
        (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
    )
    return idade


def texto_sim_nao(valor: str) -> str:
    valor_norm = normalizar_texto(valor)
    if valor_norm in ["s", "sim", "yes", "y"]:
        return "Sim"
    if valor_norm in ["n", "nao", "não", "no"]:
        return "Não"
    return valor.strip() if valor else ""


def data_hora_atual() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def data_atual() -> str:
    from datetime import date
    return date.today().strftime("%Y-%m-%d")

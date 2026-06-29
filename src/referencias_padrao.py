from src.catalogo_exames import referencias_para_cadastro, aliases_para_cadastro, cobertura_catalogo
from src.database import ler_csv
from src.exames import cadastrar_referencia_exame, cadastrar_alias_exame
from src.utils import normalizar_texto


def _ref_key(ref: dict) -> tuple:
    return (
        normalizar_texto(ref.get("nome_exame", "")),
        str(ref.get("sexo", "")),
        str(ref.get("idade_min", "")),
        str(ref.get("idade_max", "")),
        str(ref.get("unidade", "")),
    )


def carregar_referencias_padrao() -> dict:
    existentes = {_ref_key(r) for r in ler_csv("referencias_exames")}
    criadas = 0
    ignoradas = 0

    for ref in referencias_para_cadastro():
        if _ref_key(ref) in existentes:
            ignoradas += 1
            continue

        resultado = cadastrar_referencia_exame(ref, executar_analise=False)
        if resultado.get("sucesso"):
            criadas += 1
            existentes.add(_ref_key(ref))

    return {"criadas": criadas, "ignoradas": ignoradas}


def carregar_aliases_padrao() -> dict:
    existentes = {
        (normalizar_texto(a.get("alias", "")), str(a.get("nome_padronizado", "")))
        for a in ler_csv("alias_exames")
    }
    criados = 0
    ignorados = 0

    for item in aliases_para_cadastro():
        chave = (normalizar_texto(item["alias"]), item["nome_padronizado"])
        if chave in existentes:
            ignorados += 1
            continue

        resultado = cadastrar_alias_exame(item["alias"], item["nome_padronizado"])
        if resultado.get("sucesso"):
            criados += 1
            existentes.add(chave)

    return {"criados": criados, "ignorados": ignorados}


def carregar_catalogo_padrao() -> dict:
    refs = carregar_referencias_padrao()
    aliases = carregar_aliases_padrao()
    cobertura = cobertura_catalogo()
    return {"referencias": refs, "aliases": aliases, "cobertura": cobertura}

# -*- coding: utf-8 -*-
"""
Agrupamento de exames do NutriSoft.

Regras:
- A lista de exames continua completa.
- Exames são agrupados por cards macro.
- Painéis como Hemograma Completo e Lipidograma não são lançáveis.
- Dentro de cada grupo, os exames sinalizados no documento aparecem primeiro.
- Depois aparecem os demais exames do grupo em ordem alfabética.
- A única remoção permitida é exame já cadastrado para o mesmo paciente na mesma data.
"""

import unicodedata


# Títulos/painéis que NÃO devem aparecer como exame lançável.
PAINEIS_NAO_CADASTRAVEIS = {
    "Hemograma Completo": "Hemograma",
    "Lipidograma": "Perfil Lipídico",
}


GRUPOS_PADRAO = [
    "Função Renal",
    "Metabolismo Glicêmico",
    "Perfil Lipídico",
    "Função Hepática",
    "Metabolismo do Ferro",
    "Hemograma",
    "Tireoide / Hormônios",
    "Vitaminas / Imunologia",
    "Urina",
    "Fezes",
    "Microbiologia",
    "Outros",
]


EXAMES_PRIORITARIOS_POR_GRUPO = {
    "Função Renal": [
        "Creatinina",
        "Ureia",
    ],
    "Metabolismo Glicêmico": [
        "Glicose",
        "Hemoglobina Glicosilada",
        "Insulina",
    ],
    "Perfil Lipídico": [
        "Colesterol Total",
        "HDL",
        "LDL",
        "VLDL",
        "Triglicerídeos",
    ],
    "Função Hepática": [
        "TGO",
        "TGP",
    ],
    "Metabolismo do Ferro": [
        "Ferro Sérico",
        "Ferritina",
    ],
    "Hemograma": [
        "Hemácias",
        "Hemoglobina",
        "Hematócrito",
        "VCM",
        "HCM",
        "CHCM",
        "RDW",
        "Leucócitos",
        "Plaquetas",
    ],
    "Tireoide / Hormônios": [
        "TSH",
        "T4 Livre",
    ],
    "Vitaminas / Imunologia": [
        "Vitamina B12",
        "25OH D3",
    ],
    "Urina": [
        "E.A.S.",
    ],
}


def normalizar_texto(valor):
    texto = str(valor or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.replace(".", " ").replace("-", " ").replace("_", " ")
    return " ".join(texto.split())


def obter_nome_exame_item(item):
    if isinstance(item, dict):
        for chave in ("nome", "exame", "nome_exame", "descricao", "label", "text"):
            valor = item.get(chave)
            if valor:
                return str(valor).strip()

        valor = item.get("id")
        if valor:
            return str(valor).strip()

    return str(item or "").strip()


def eh_painel_nao_cadastravel(nome_exame):
    nome_norm = normalizar_texto(nome_exame)
    return any(
        normalizar_texto(painel) == nome_norm
        for painel in PAINEIS_NAO_CADASTRAVEIS
    )


def grupo_do_painel(nome_exame):
    nome_norm = normalizar_texto(nome_exame)

    for painel, grupo in PAINEIS_NAO_CADASTRAVEIS.items():
        if normalizar_texto(painel) == nome_norm:
            return grupo

    return None


def identificar_grupo_exame(nome_exame):
    nome_original = str(nome_exame or "").strip()
    nome = normalizar_texto(nome_original)

    grupo_painel = grupo_do_painel(nome_original)
    if grupo_painel:
        return grupo_painel

    for grupo, exames in EXAMES_PRIORITARIOS_POR_GRUPO.items():
        for exame in exames:
            if normalizar_texto(exame) == nome:
                return grupo

    regras = [
        ("Função Renal", [
            "creatinina", "ureia", "clearance", "taxa de filtracao",
            "taxa de filtração", "egfr", "tfg",
        ]),
        ("Metabolismo Glicêmico", [
            "glicose", "hemoglobina glicosilada", "hba1c", "insulina",
            "homa", "peptideo c", "peptídeo c",
        ]),
        ("Perfil Lipídico", [
            "colesterol", "hdl", "ldl", "vldl", "triglicerideos",
            "triglicerídeos", "lipidograma", "lipoproteina", "lipoproteína",
        ]),
        ("Função Hepática", [
            "tgo", "ast", "tgp", "alt", "gama gt", "ggt", "fosfatase",
            "bilirrubina", "albumina", "proteinas totais", "proteínas totais",
        ]),
        ("Metabolismo do Ferro", [
            "ferro", "ferritina", "transferrina", "saturacao de transferrina",
            "saturação de transferrina",
        ]),
        ("Hemograma", [
            "hemograma", "hemacias", "hemácias", "eritrocitos", "eritrócitos",
            "hemoglobina", "hematocrito", "hematócrito", "vcm", "hcm",
            "chcm", "rdw", "leucocitos", "leucócitos", "plaquetas",
            "neutrofilos", "neutrófilos", "linfocitos", "linfócitos",
            "monocitos", "monócitos", "eosinofilos", "eosinófilos",
            "basofilos", "basófilos",
        ]),
        ("Tireoide / Hormônios", [
            "tsh", "t4", "t3", "testosterona", "cortisol", "estradiol",
            "progesterona", "prolactina", "lh", "fsh", "dhea",
        ]),
        ("Vitaminas / Imunologia", [
            "vitamina", "b12", "25oh", "25 oh", "vitamina d", "anti",
            "igg", "igm", "ige", "pcr", "proteina c reativa",
            "proteína c reativa",
        ]),
        ("Urina", [
            "eas", "e a s", "urina", "urocultura", "sedimento urinario",
            "sedimento urinário",
        ]),
        ("Fezes", [
            "fezes", "coprocultura", "parasitologico", "parasitológico",
        ]),
        ("Microbiologia", [
            "cultura", "antibiograma", "bacterioscopia", "microbiologia",
        ]),
    ]

    for grupo, palavras in regras:
        for palavra in palavras:
            if normalizar_texto(palavra) in nome:
                return grupo

    return "Outros"


def identificar_grupo_item(item):
    nome = obter_nome_exame_item(item)

    if isinstance(item, dict):
        grupo = str(item.get("grupo") or "").strip()
        if grupo in GRUPOS_PADRAO:
            return grupo

    return identificar_grupo_exame(nome)


def listar_grupos_disponiveis(exames=None):
    if not exames:
        return GRUPOS_PADRAO

    grupos = []

    for exame in exames:
        nome = obter_nome_exame_item(exame)

        if eh_painel_nao_cadastravel(nome):
            grupo = grupo_do_painel(nome)
        else:
            grupo = identificar_grupo_item(exame)

        if grupo and grupo not in grupos:
            grupos.append(grupo)

    return sorted(
        grupos,
        key=lambda grupo: GRUPOS_PADRAO.index(grupo)
        if grupo in GRUPOS_PADRAO else 999
    )


def ordem_prioridade_no_grupo(nome_exame, grupo):
    prioritarios = EXAMES_PRIORITARIOS_POR_GRUPO.get(grupo, [])
    nome_normalizado = normalizar_texto(nome_exame)

    for indice, exame_prioritario in enumerate(prioritarios):
        if normalizar_texto(exame_prioritario) == nome_normalizado:
            return indice

    return None


def item_cadastravel(item):
    nome = obter_nome_exame_item(item)
    return bool(nome) and not eh_painel_nao_cadastravel(nome)


def ordenar_exames_por_prioridade(exames, grupo=None, exames_ja_cadastrados=None):
    exames = list(exames or [])
    exames_ja_cadastrados = exames_ja_cadastrados or []

    ja_cadastrados_normalizados = {
        normalizar_texto(obter_nome_exame_item(exame))
        for exame in exames_ja_cadastrados
    }

    filtrados = []

    for exame in exames:
        nome = obter_nome_exame_item(exame)

        if not nome:
            continue

        if eh_painel_nao_cadastravel(nome):
            continue

        if normalizar_texto(nome) in ja_cadastrados_normalizados:
            continue

        grupo_exame = identificar_grupo_exame(nome)

        if grupo and grupo_exame != grupo:
            continue

        filtrados.append(nome)

    def chave_ordenacao(nome):
        grupo_exame = identificar_grupo_exame(nome)
        grupo_rank = (
            GRUPOS_PADRAO.index(grupo_exame)
            if grupo_exame in GRUPOS_PADRAO
            else 999
        )

        prioridade = ordem_prioridade_no_grupo(nome, grupo_exame)

        if prioridade is not None:
            return (grupo_rank, 0, prioridade, normalizar_texto(nome))

        return (grupo_rank, 1, 9999, normalizar_texto(nome))

    return sorted(filtrados, key=chave_ordenacao)


def ordenar_itens_exames_por_prioridade(itens, grupo=None, exames_ja_cadastrados=None):
    itens = list(itens or [])
    exames_ja_cadastrados = exames_ja_cadastrados or []

    ja_cadastrados_normalizados = {
        normalizar_texto(obter_nome_exame_item(exame))
        for exame in exames_ja_cadastrados
    }

    filtrados = []

    for item in itens:
        nome = obter_nome_exame_item(item)

        if not nome:
            continue

        if eh_painel_nao_cadastravel(nome):
            continue

        if normalizar_texto(nome) in ja_cadastrados_normalizados:
            continue

        grupo_item = identificar_grupo_item(item)

        if grupo and grupo_item != grupo:
            continue

        filtrados.append(item)

    def chave_ordenacao(item):
        nome = obter_nome_exame_item(item)
        grupo_item = identificar_grupo_item(item)

        grupo_rank = (
            GRUPOS_PADRAO.index(grupo_item)
            if grupo_item in GRUPOS_PADRAO
            else 999
        )

        prioridade = ordem_prioridade_no_grupo(nome, grupo_item)

        if prioridade is not None:
            return (grupo_rank, 0, prioridade, normalizar_texto(nome))

        return (grupo_rank, 1, 9999, normalizar_texto(nome))

    return sorted(filtrados, key=chave_ordenacao)


def agrupar_itens_exames(itens, exames_ja_cadastrados=None):
    itens_ordenados = ordenar_itens_exames_por_prioridade(
        itens,
        grupo=None,
        exames_ja_cadastrados=exames_ja_cadastrados,
    )

    grupos = []

    for grupo in GRUPOS_PADRAO:
        itens_grupo = [
            item for item in itens_ordenados
            if identificar_grupo_item(item) == grupo
        ]

        if itens_grupo:
            grupos.append((grupo, itens_grupo))

    return grupos


def garantir_prioritarios_no_catalogo(catalogo):
    catalogo = list(catalogo or [])

    existentes = {
        normalizar_texto(obter_nome_exame_item(item))
        for item in catalogo
    }

    proximos_ids = []

    for item in catalogo:
        if isinstance(item, dict):
            try:
                proximos_ids.append(int(item.get("id")))
            except Exception:
                pass

    proximo_id = max(proximos_ids, default=0) + 1

    metadados = {
        "Creatinina": ("Função Renal", "0,7 - 1,3 mg/dL", "KDIGO / valores laboratoriais usuais"),
        "Ureia": ("Função Renal", "10 - 50 mg/dL", "Valores laboratoriais usuais"),
        "Glicose": ("Metabolismo Glicêmico", "70 - 99 mg/dL", "Diretrizes da Sociedade Brasileira de Diabetes"),
        "Hemoglobina Glicosilada": ("Metabolismo Glicêmico", "< 5,7 %", "Diretrizes da Sociedade Brasileira de Diabetes"),
        "Insulina": ("Metabolismo Glicêmico", "2 - 25 µUI/mL", "Valores laboratoriais usuais"),
        "Colesterol Total": ("Perfil Lipídico", "< 190 mg/dL", "Diretriz Brasileira de Dislipidemias"),
        "HDL": ("Perfil Lipídico", "> 40 mg/dL", "Diretriz Brasileira de Dislipidemias"),
        "LDL": ("Perfil Lipídico", "< 130 mg/dL", "Diretriz Brasileira de Dislipidemias"),
        "VLDL": ("Perfil Lipídico", "5 - 40 mg/dL", "Valores laboratoriais usuais"),
        "Triglicerídeos": ("Perfil Lipídico", "< 150 mg/dL", "Diretriz Brasileira de Dislipidemias"),
        "TGO": ("Função Hepática", "até 40 U/L", "Valores laboratoriais usuais"),
        "TGP": ("Função Hepática", "até 41 U/L", "Valores laboratoriais usuais"),
        "Ferro Sérico": ("Metabolismo do Ferro", "60 - 170 µg/dL", "Valores laboratoriais usuais"),
        "Ferritina": ("Metabolismo do Ferro", "Conforme sexo e idade", "Valores laboratoriais usuais"),
        "Hemácias": ("Hemograma", "Conforme sexo e idade", "Valores laboratoriais usuais"),
        "Hemoglobina": ("Hemograma", "13,0 - 17,0 g/dL", "Valores laboratoriais usuais"),
        "Hematócrito": ("Hemograma", "40 - 52 %", "Valores laboratoriais usuais"),
        "VCM": ("Hemograma", "80 - 100 fL", "Valores laboratoriais usuais"),
        "HCM": ("Hemograma", "27 - 33 pg", "Valores laboratoriais usuais"),
        "CHCM": ("Hemograma", "32 - 36 g/dL", "Valores laboratoriais usuais"),
        "RDW": ("Hemograma", "11,5 - 14,5 %", "Valores laboratoriais usuais"),
        "Leucócitos": ("Hemograma", "4.000 - 11.000/mm³", "Valores laboratoriais usuais"),
        "Plaquetas": ("Hemograma", "150.000 - 450.000/mm³", "Valores laboratoriais usuais"),
        "TSH": ("Tireoide / Hormônios", "0,4 - 4,0 µUI/mL", "Valores laboratoriais usuais"),
        "T4 Livre": ("Tireoide / Hormônios", "0,8 - 1,8 ng/dL", "Valores laboratoriais usuais"),
        "Vitamina B12": ("Vitaminas / Imunologia", "200 - 900 pg/mL", "Valores laboratoriais usuais"),
        "25OH D3": ("Vitaminas / Imunologia", "30 - 100 ng/mL", "Valores laboratoriais usuais"),
        "E.A.S.": ("Urina", "Avaliação qualitativa", "Valores laboratoriais usuais"),
    }

    for grupo, exames in EXAMES_PRIORITARIOS_POR_GRUPO.items():
        for exame in exames:
            if normalizar_texto(exame) in existentes:
                continue

            categoria, referencia, fonte = metadados.get(
                exame,
                (grupo, "Referência conforme laboratório", "Valores laboratoriais usuais"),
            )

            catalogo.append({
                "id": str(proximo_id),
                "nome": exame,
                "grupo": grupo,
                "categoria": categoria,
                "referencia": referencia,
                "fonte": fonte,
            })

            existentes.add(normalizar_texto(exame))
            proximo_id += 1

    return catalogo

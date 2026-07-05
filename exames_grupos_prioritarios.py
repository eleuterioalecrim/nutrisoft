# -*- coding: utf-8 -*-
"""
Configuração central dos grupos de exames do NutriSoft.

Organiza exames por grupos e coloca como primeira opção, dentro de cada grupo,
os exames marcados no documento de solicitação.
"""

import unicodedata


EXAMES_PRIORITARIOS_POR_GRUPO = {
    "Bioquímica": [
        "Creatinina",
        "Ferro Sérico",
        "Glicose",
        "Hemoglobina Glicosilada",
        "Lipidograma",
        "TGO",
        "TGP",
        "Ureia",
    ],
    "Imunologia": [
        "Vitamina B12",
        "25OH D3",
    ],
    "Hematologia": [
        "Hemograma Completo",
    ],
    "Hormônios": [
        "TSH",
        "Ferritina",
        "T4 Livre",
        "Insulina",
    ],
    "Urina": [
        "E.A.S.",
    ],
}


GRUPOS_PADRAO = [
    "Bioquímica",
    "Hematologia",
    "Hormônios",
    "Imunologia",
    "Urina",
    "Fezes",
    "Microbiologia",
    "Outros",
]


def normalizar_texto(valor):
    texto = str(valor or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.replace(".", "").replace("-", " ").replace("_", " ")
    return " ".join(texto.split())


def identificar_grupo_exame(nome_exame):
    nome = normalizar_texto(nome_exame)

    for grupo, exames in EXAMES_PRIORITARIOS_POR_GRUPO.items():
        for exame in exames:
            if normalizar_texto(exame) == nome:
                return grupo

    regras = [
        ("Bioquímica", [
            "glicose", "creatinina", "ureia", "tgo", "tgp",
            "colesterol", "triglicerideos", "lipidograma",
            "hdl", "ldl", "vldl", "ferro", "acido urico",
            "bilirrubina", "fosfatase", "gama gt", "albumina",
            "sodio", "potassio", "calcio", "magnesio",
        ]),
        ("Hematologia", [
            "hemograma", "hemoglobina", "hematocrito",
            "leucocitos", "plaquetas", "vcm", "hcm", "chcm", "rdw",
        ]),
        ("Hormônios", [
            "tsh", "t4", "t3", "insulina", "ferritina",
            "testosterona", "cortisol", "estradiol",
            "progesterona", "prolactina", "lh", "fsh",
        ]),
        ("Imunologia", [
            "vitamina b12", "25oh", "vitamina d",
            "anti", "igg", "igm", "ige", "pcr",
            "proteina c reativa",
        ]),
        ("Urina", [
            "eas", "urina", "urocultura", "sedimento urinario",
        ]),
        ("Fezes", [
            "fezes", "coprocultura", "parasitologico",
        ]),
        ("Microbiologia", [
            "cultura", "antibiograma", "bacterioscopia", "microbiologia",
        ]),
    ]

    for grupo, palavras in regras:
        for palavra in palavras:
            if palavra in nome:
                return grupo

    return "Outros"


def listar_grupos_disponiveis(exames=None):
    if not exames:
        return GRUPOS_PADRAO

    grupos = []
    for exame in exames:
        grupo = identificar_grupo_exame(exame)
        if grupo not in grupos:
            grupos.append(grupo)

    return sorted(
        grupos,
        key=lambda grupo: GRUPOS_PADRAO.index(grupo)
        if grupo in GRUPOS_PADRAO else 999
    )


def ordenar_exames_por_prioridade(exames, grupo=None, exames_ja_cadastrados=None):
    exames = list(exames or [])
    exames_ja_cadastrados = exames_ja_cadastrados or []

    ja_cadastrados_normalizados = {
        normalizar_texto(exame)
        for exame in exames_ja_cadastrados
    }

    prioritarios = EXAMES_PRIORITARIOS_POR_GRUPO.get(grupo, []) if grupo else []

    ordem_prioritarios = {
        normalizar_texto(exame): indice
        for indice, exame in enumerate(prioritarios)
    }

    exames_filtrados = []

    for exame in exames:
        exame_texto = str(exame or "").strip()

        if not exame_texto:
            continue

        exame_normalizado = normalizar_texto(exame_texto)

        if exame_normalizado in ja_cadastrados_normalizados:
            continue

        grupo_exame = identificar_grupo_exame(exame_texto)

        if grupo and grupo_exame != grupo:
            continue

        exames_filtrados.append(exame_texto)

    def chave_ordenacao(exame):
        exame_normalizado = normalizar_texto(exame)

        if exame_normalizado in ordem_prioritarios:
            return (0, ordem_prioritarios[exame_normalizado], exame_normalizado)

        return (1, 9999, exame_normalizado)

    return sorted(exames_filtrados, key=chave_ordenacao)

def obter_nome_exame_item(item):
    """
    Extrai o nome do exame a partir de string ou dicionário de catálogo.
    """
    if isinstance(item, dict):
        for chave in ("nome", "exame", "nome_exame", "descricao", "label", "text"):
            valor = item.get(chave)
            if valor:
                return str(valor).strip()

        # fallback seguro: usa id se não houver nome
        valor = item.get("id")
        if valor:
            return str(valor).strip()

    return str(item or "").strip()


def ordenar_itens_exames_por_prioridade(itens, grupo=None, exames_ja_cadastrados=None):
    """
    Ordena uma lista de itens de catálogo preservando os objetos originais.

    Diferente de ordenar_exames_por_prioridade(), esta função aceita:
    - strings;
    - dicionários do CATALOGO_EXAMES;
    - qualquer objeto que possa ser convertido para texto.

    Retorna os próprios itens originais, apenas reordenados e filtrados.
    """
    itens = list(itens or [])
    exames_ja_cadastrados = exames_ja_cadastrados or []

    ja_cadastrados_normalizados = {
        normalizar_texto(obter_nome_exame_item(exame))
        for exame in exames_ja_cadastrados
    }

    prioritarios = EXAMES_PRIORITARIOS_POR_GRUPO.get(grupo, []) if grupo else []

    ordem_prioritarios = {
        normalizar_texto(exame): indice
        for indice, exame in enumerate(prioritarios)
    }

    filtrados = []

    for item in itens:
        nome = obter_nome_exame_item(item)

        if not nome:
            continue

        nome_normalizado = normalizar_texto(nome)

        if nome_normalizado in ja_cadastrados_normalizados:
            continue

        grupo_exame = identificar_grupo_exame(nome)

        if grupo and grupo_exame != grupo:
            continue

        filtrados.append(item)

    def chave_ordenacao(item):
        nome = obter_nome_exame_item(item)
        nome_normalizado = normalizar_texto(nome)

        if nome_normalizado in ordem_prioritarios:
            return (0, ordem_prioritarios[nome_normalizado], nome_normalizado)

        return (1, 9999, nome_normalizado)

    return sorted(filtrados, key=chave_ordenacao)


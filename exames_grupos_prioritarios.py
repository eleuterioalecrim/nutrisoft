# -*- coding: utf-8 -*-
"""
Agrupamento de exames do NutriSoft.

Regra:
- A lista de exames deve continuar completa.
- Os exames são agrupados por categoria.
- Dentro de cada grupo, os exames prioritários aparecem primeiro.
- Os demais exames do grupo aparecem depois, em ordem alfabética.
- A única exclusão permitida é a de exames já cadastrados para o paciente na mesma data.
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


def obter_nome_exame_item(item):
    """
    Extrai o nome do exame a partir de string ou dicionário de catálogo.
    """
    if isinstance(item, dict):
        for chave in ("nome", "exame", "nome_exame", "descricao", "label", "text"):
            valor = item.get(chave)
            if valor:
                return str(valor).strip()

        valor = item.get("id")
        if valor:
            return str(valor).strip()

    return str(item or "").strip()


def identificar_grupo_exame(nome_exame):
    """
    Identifica o grupo do exame.

    Primeiro verifica os exames prioritários.
    Depois usa palavras-chave.
    Se não encontrar, classifica como Outros.
    """
    nome = normalizar_texto(nome_exame)

    for grupo, exames in EXAMES_PRIORITARIOS_POR_GRUPO.items():
        for exame in exames:
            if normalizar_texto(exame) == nome:
                return grupo

    regras = [
        ("Bioquímica", [
            "glicose", "creatinina", "ureia", "tgo", "tgp",
            "colesterol", "triglicerideos", "triglicerídeos",
            "lipidograma", "hdl", "ldl", "vldl", "ferro",
            "acido urico", "ácido úrico", "bilirrubina",
            "fosfatase", "gama gt", "albumina", "proteinas totais",
            "proteínas totais", "sodio", "sódio", "potassio",
            "potássio", "calcio", "cálcio", "magnesio", "magnésio",
        ]),
        ("Hematologia", [
            "hemograma", "hemoglobina", "hematocrito", "hematócrito",
            "leucocitos", "leucócitos", "plaquetas", "vcm", "hcm",
            "chcm", "rdw", "eritrocitos", "eritrócitos",
        ]),
        ("Hormônios", [
            "tsh", "t4", "t3", "insulina", "ferritina",
            "testosterona", "cortisol", "estradiol", "progesterona",
            "prolactina", "lh", "fsh", "dhea",
        ]),
        ("Imunologia", [
            "vitamina b12", "25oh", "vitamina d", "anti", "igg",
            "igm", "ige", "pcr", "proteina c reativa",
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
    """
    Identifica o grupo de um item de catálogo.
    Se o dicionário já tiver grupo válido, usa esse grupo.
    Caso contrário, identifica pelo nome.
    """
    if isinstance(item, dict):
        grupo = str(item.get("grupo") or "").strip()
        if grupo in GRUPOS_PADRAO:
            return grupo

    return identificar_grupo_exame(obter_nome_exame_item(item))


def listar_grupos_disponiveis(exames=None):
    if not exames:
        return GRUPOS_PADRAO

    grupos = []

    for exame in exames:
        grupo = identificar_grupo_item(exame)
        if grupo not in grupos:
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


def ordenar_exames_por_prioridade(exames, grupo=None, exames_ja_cadastrados=None):
    """
    Ordena nomes de exames mantendo a lista completa.

    Se grupo for informado:
    - retorna todos os exames daquele grupo;
    - prioritários primeiro;
    - demais depois em ordem alfabética.

    Se grupo não for informado:
    - retorna todos os exames;
    - agrupados por grupo;
    - dentro de cada grupo, prioritários primeiro;
    - demais depois em ordem alfabética.

    Não remove exames comuns.
    Remove apenas exames já cadastrados, quando exames_ja_cadastrados for informado.
    """
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
    """
    Ordena itens de catálogo preservando os objetos originais.

    Aceita:
    - strings;
    - dicionários do CATALOGO_EXAMES;
    - objetos convertíveis para texto.

    Mantém todos os exames, exceto os já cadastrados quando informados.
    """
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

# -*- coding: utf-8 -*-
"""
Diagnóstico nutricional do NutriSoft.

Regra principal:
- A análise dos exames deve considerar ALTERAÇÃO apenas quando o resultado
  estiver fora da referência laboratorial.
- Valores dentro da referência não devem entrar como alteração.
- Faixas funcionais/ideais não devem inflar o número de alterações.
"""

import re
import unicodedata


def normalizar_texto(valor):
    texto = str(valor or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return " ".join(texto.split())


def extrair_numero(valor, nome_exame=""):
    """
    Extrai número com suporte a:
    - decimal brasileiro: 0,18
    - decimal internacional: 0.18
    - milhar brasileiro: 143.000
    - densidade urinária: 1.033 deve permanecer 1.033, não 1033
    """
    if valor is None:
        return None

    texto = str(valor).strip()
    nome_norm = normalizar_texto(nome_exame)

    m = re.search(r"-?\d+(?:[.,]\d+)?", texto)
    if not m:
        return None

    numero = m.group(0)

    try:
        if "," in numero:
            numero = numero.replace(".", "").replace(",", ".")
            return float(numero)

        if "." in numero:
            parte_inteira, parte_decimal = numero.split(".", 1)

            # Densidade urinária costuma vir como 1.033.
            if "densidade" in nome_norm or "urina" in nome_norm:
                return float(numero)

            # Decimal com ponto: 0.87, 5.4, 1.2, 28.7.
            if len(parte_decimal) <= 2:
                return float(numero)

            # Heurística para milhar: 4.510 leucócitos, 143.000 plaquetas.
            if len(parte_decimal) == 3 and int(parte_inteira or "0") >= 2:
                return float(parte_inteira + parte_decimal)

            return float(numero)

        return float(numero)
    except Exception:
        return None


ALIASES_EXAMES = {
    "bilirrubina indireta": [
        "bilirrubina indireta",
        "indireta",
    ],
    "colesterol total": [
        "colesterol total",
    ],
    "plaquetas": [
        "plaquetas",
        "total de plaquetas",
    ],
    "urina densidade": [
        "urina densidade",
        "densidade urinaria",
        "densidade urinária",
        "densidade",
    ],
    "creatinina": [
        "creatinina",
    ],
    "ferritina": [
        "ferritina",
    ],
    "glicose": [
        "glicose",
        "glicose jejum",
        "glicose em jejum",
    ],
    "hemoglobina glicada": [
        "hemoglobina glicada",
        "hemoglobina glicosilada",
        "hba1c",
        "a1c",
    ],
    "insulina": [
        "insulina",
        "insulina jejum",
        "insulina em jejum",
    ],
    "hdl": [
        "hdl",
        "hdl colesterol",
        "hdl-colesterol",
    ],
    "ldl": [
        "ldl",
        "ldl colesterol",
        "ldl-colesterol",
    ],
    "vldl": [
        "vldl",
        "vldl colesterol",
        "vldl-colesterol",
    ],
    "triglicerideos": [
        "triglicerideos",
        "triglicerídeos",
        "triglicerides",
        "triglicérides",
    ],
    "nao hdl": [
        "nao hdl",
        "não hdl",
        "nao hdl colesterol",
        "não-hdl-colesterol",
    ],
    "hemoglobina": [
        "hemoglobina",
    ],
    "hematocrito": [
        "hematocrito",
        "hematócrito",
    ],
    "hemacias": [
        "hemacias",
        "hemácias",
        "eritrocitos",
        "eritrócitos",
    ],
    "hcm": [
        "hcm",
        "hemoglobina corpuscular media",
        "hemoglobina corpuscular média",
    ],
    "vcm": [
        "vcm",
        "volume corpuscular medio",
        "volume corpuscular médio",
    ],
    "chcm": [
        "chcm",
        "concentracao de hemoglobina corpuscular media",
        "concentração de hemoglobina corpuscular média",
    ],
    "rdw": [
        "rdw",
        "coeficiente de variacao do volume eritrocitario",
        "coeficiente de variação do volume eritrocitário",
    ],
    "leucocitos": [
        "leucocitos",
        "leucócitos",
    ],
    "tgo": [
        "tgo",
        "ast",
        "tgo ast",
        "transaminase glutamico oxalacetica",
        "aspartato amino transferase",
    ],
    "tgp": [
        "tgp",
        "alt",
        "tgp alt",
        "transaminase glutamico piruvica",
        "alanina amino transferase",
    ],
    "tsh": [
        "tsh",
        "hormonio tiroestimulante",
        "hormônio tiroestimulante",
    ],
    "t4 livre": [
        "t4 livre",
        "tiroxina t4 livre",
        "tiroxina livre",
    ],
    "ureia": [
        "ureia",
    ],
    "vitamina b12": [
        "vitamina b12",
        "vitamina b 12",
        "b12",
    ],
    "vitamina d": [
        "vitamina d",
        "25 hidroxi vitamina d",
        "25oh d3",
        "25 oh d3",
    ],
    "magnesio": [
        "magnesio",
        "magnésio",
        "magnesio serico",
        "magnésio sérico",
    ],
    "potassio": [
        "potassio",
        "potássio",
    ],
    "sodio": [
        "sodio",
        "sódio",
    ],
    "proteina c reativa": [
        "proteina c reativa",
        "proteína c reativa",
        "pcr",
    ],
}


DISPLAY_EXAMES = {
    "bilirrubina indireta": "Bilirrubina indireta",
    "colesterol total": "Colesterol total",
    "plaquetas": "Plaquetas",
    "urina densidade": "Densidade urinária",
    "hemoglobina glicada": "Hemoglobina glicada",
    "creatinina": "Creatinina",
    "ferritina": "Ferritina",
    "glicose": "Glicose",
    "insulina": "Insulina",
    "hdl": "HDL",
    "ldl": "LDL",
    "vldl": "VLDL",
    "triglicerideos": "Triglicerídeos",
    "nao hdl": "Não-HDL",
    "hemoglobina": "Hemoglobina",
    "hematocrito": "Hematócrito",
    "hemacias": "Hemácias",
    "hcm": "HCM",
    "vcm": "VCM",
    "chcm": "CHCM",
    "rdw": "RDW",
    "leucocitos": "Leucócitos",
    "tgo": "TGO / AST",
    "tgp": "TGP / ALT",
    "tsh": "TSH",
    "t4 livre": "T4 livre",
    "ureia": "Ureia",
    "vitamina b12": "Vitamina B12",
    "vitamina d": "Vitamina D",
    "magnesio": "Magnésio",
    "potassio": "Potássio",
    "sodio": "Sódio",
    "proteina c reativa": "Proteína C-reativa",
}


REGRAS_EXAMES = {
    "bilirrubina indireta": {
        "unidade": "mg/dL",
        "ref_min": 0.20,
        "ref_max": 0.80,
        "baixo": "Bilirrubina indireta abaixo da referência. Geralmente tem menor peso clínico isolado, mas deve ser interpretada junto ao painel hepático.",
        "alto": "Bilirrubina indireta acima da referência. Avaliar hemólise, síndrome de Gilbert, função hepática e contexto clínico.",
        "conduta_baixo": "Correlacionar com bilirrubina total, direta, TGO, TGP, GGT e sinais clínicos. Em geral, acompanhar evolução.",
        "conduta_alto": "Avaliar painel hepático completo e encaminhar para avaliação médica se persistente ou sintomático.",
        "complementares": "Bilirrubina total e direta, TGO, TGP, GGT, hemograma, reticulócitos conforme contexto.",
    },
    "colesterol total": {
        "unidade": "mg/dL",
        "ref_min": None,
        "ref_max": 190,
        "baixo": "Colesterol total baixo. Avaliar contexto nutricional, tireoide, absorção e ingestão alimentar se muito reduzido.",
        "alto": "Colesterol total acima da referência. Pode indicar dislipidemia e aumento de risco cardiovascular, dependendo do conjunto do perfil lipídico.",
        "conduta_baixo": "Avaliar ingestão alimentar, peso, tireoide e absorção conforme contexto.",
        "conduta_alto": "Ajustar qualidade das gorduras, fibras, ultraprocessados, açúcar e rotina de atividade física. Avaliar LDL, HDL, triglicerídeos e risco global.",
        "complementares": "LDL, HDL, triglicerídeos, não-HDL, ApoB, glicose, HbA1c, TGO/TGP.",
    },
    "plaquetas": {
        "unidade": "/mm³",
        "ref_min": 151000,
        "ref_max": 304000,
        "baixo": "Plaquetas abaixo da referência. Pode indicar trombocitopenia leve, variação laboratorial ou condição hematológica conforme contexto.",
        "alto": "Plaquetas acima da referência. Pode estar relacionado a inflamação, deficiência de ferro ou resposta reacional.",
        "conduta_baixo": "Reavaliar histórico, sangramentos, uso de medicamentos e repetir hemograma conforme orientação profissional.",
        "conduta_alto": "Cruzar com ferritina, PCR e sinais inflamatórios. Acompanhar evolução.",
        "complementares": "Hemograma de controle, ferritina, PCR-us, avaliação médica se persistente ou sintomático.",
    },
    "urina densidade": {
        "unidade": "densidade",
        "ref_min": 1.010,
        "ref_max": 1.030,
        "baixo": "Densidade urinária abaixo da referência. Pode indicar urina muito diluída ou alteração de concentração urinária conforme contexto.",
        "alto": "Densidade urinária acima da referência. Pode sugerir urina concentrada, baixa ingestão hídrica ou perda hídrica.",
        "conduta_baixo": "Correlacionar com hidratação, função renal e sintomas urinários.",
        "conduta_alto": "Aumentar hidratação de forma progressiva e reavaliar urina. Cruzar com rotina de treino, sudorese e consumo hídrico.",
        "complementares": "Urina tipo I de controle, ureia, creatinina, eletrólitos e avaliação clínica se persistente.",
    },

    "creatinina": {"unidade": "mg/dL", "ref_min": 0.70, "ref_max": 1.30},
    "ferritina": {"unidade": "ng/mL", "ref_min": 26, "ref_max": 446},
    "glicose": {"unidade": "mg/dL", "ref_min": 70, "ref_max": 99},
    "hemoglobina glicada": {"unidade": "%", "ref_min": None, "ref_max": 5.7},
    "insulina": {"unidade": "mU/L", "ref_min": 2, "ref_max": 13},
    "hdl": {"unidade": "mg/dL", "ref_min": 40, "ref_max": None},
    "ldl": {"unidade": "mg/dL", "ref_min": None, "ref_max": 130},
    "vldl": {"unidade": "mg/dL", "ref_min": None, "ref_max": 30},
    "triglicerideos": {"unidade": "mg/dL", "ref_min": None, "ref_max": 150},
    "nao hdl": {"unidade": "mg/dL", "ref_min": None, "ref_max": 160},
    "hemoglobina": {"unidade": "g/dL", "ref_min": 13.3, "ref_max": 16.5},
    "hematocrito": {"unidade": "%", "ref_min": 39.2, "ref_max": 49.0},
    "hemacias": {"unidade": "milhões/mm³", "ref_min": 4.32, "ref_max": 5.67},
    "hcm": {"unidade": "pg", "ref_min": 27.7, "ref_max": 32.7},
    "vcm": {"unidade": "fL", "ref_min": 81.7, "ref_max": 95.3},
    "chcm": {"unidade": "g/dL", "ref_min": 32.4, "ref_max": 36.0},
    "rdw": {"unidade": "%", "ref_min": 11.8, "ref_max": 14.1},
    "leucocitos": {"unidade": "/mm³", "ref_min": 3650, "ref_max": 8120},
    "tgo": {"unidade": "U/L", "ref_min": None, "ref_max": 50},
    "tgp": {"unidade": "U/L", "ref_min": None, "ref_max": 50},
    "tsh": {"unidade": "mUI/L", "ref_min": 0.45, "ref_max": 4.5},
    "t4 livre": {"unidade": "ng/dL", "ref_min": 0.9, "ref_max": 1.7},
    "ureia": {"unidade": "mg/dL", "ref_min": 10, "ref_max": 50},
    "vitamina b12": {"unidade": "ng/L", "ref_min": 300, "ref_max": None},
    "vitamina d": {"unidade": "ng/mL", "ref_min": 30, "ref_max": 100},
    "magnesio": {"unidade": "mg/dL", "ref_min": 1.6, "ref_max": 2.6},
    "potassio": {"unidade": "mEq/L", "ref_min": 3.5, "ref_max": 5.1},
    "sodio": {"unidade": "mEq/L", "ref_min": 136, "ref_max": 145},
    "proteina c reativa": {"unidade": "mg/dL", "ref_min": None, "ref_max": 1.0},
}


def completar_textos_padrao(chave, regra):
    nome = chave.replace("_", " ").title()

    regra.setdefault("baixo", f"{nome} abaixo da referência laboratorial.")
    regra.setdefault("alto", f"{nome} acima da referência laboratorial.")
    regra.setdefault("conduta_baixo", "Correlacionar com sintomas, histórico, alimentação, medicamentos e evolução. Reavaliar conforme orientação profissional.")
    regra.setdefault("conduta_alto", "Correlacionar com sintomas, histórico, alimentação, medicamentos e evolução. Reavaliar conforme orientação profissional.")
    regra.setdefault("complementares", "Avaliar exames relacionados e repetir conforme contexto clínico.")
    return regra



# Ajustes de texto para evitar redundância nos insights e no PDF.
AJUSTES_TEXTOS_EXAMES_ALTERADOS = {
    "bilirrubina indireta": {
        "baixo": "Achado isolado de menor peso clínico; acompanhar junto ao painel hepático.",
        "alto": "Elevação que deve ser correlacionada com painel hepático, hemólise e contexto clínico.",
        "conduta_baixo": "Correlacionar com bilirrubina total/direta, TGO, TGP, GGT e evolução clínica.",
        "conduta_alto": "Avaliar bilirrubina total/direta, TGO, TGP, GGT, hemograma e sinais clínicos.",
        "complementares": "Bilirrubina total/direta, TGO, TGP, GGT e hemograma, se necessário.",
    },
    "colesterol total": {
        "baixo": "Abaixo do esperado; avaliar contexto nutricional, tireoide, absorção e ingestão alimentar se muito reduzido.",
        "alto": "Acima do desejável; ponto de atenção cardiometabólico conforme perfil lipídico completo.",
        "conduta_baixo": "Avaliar dieta, peso, tireoide e absorção conforme contexto.",
        "conduta_alto": "Ajustar fibras, qualidade das gorduras, açúcar/ultraprocessados e rotina de atividade física.",
        "complementares": "LDL, HDL, triglicerídeos, não-HDL e ApoB, se disponível.",
    },
    "plaquetas": {
        "baixo": "Contagem abaixo da referência; pode ser variação laboratorial ou trombocitopenia leve conforme contexto.",
        "alto": "Contagem acima da referência; pode estar associada a inflamação, deficiência de ferro ou resposta reacional.",
        "conduta_baixo": "Verificar sangramentos, medicamentos e repetir hemograma conforme orientação profissional.",
        "conduta_alto": "Cruzar com ferritina, PCR e sinais inflamatórios; acompanhar evolução.",
        "complementares": "Hemograma de controle; avaliação médica se persistente ou sintomático.",
    },
    "urina densidade": {
        "baixo": "Urina muito diluída; correlacionar com hidratação, função renal e sintomas.",
        "alto": "Urina concentrada; sugere hidratação insuficiente ou maior perda hídrica.",
        "conduta_baixo": "Correlacionar com ingestão hídrica, função renal e sintomas urinários.",
        "conduta_alto": "Reforçar hidratação e cruzar com treino, sudorese e consumo hídrico.",
        "complementares": "Urina tipo I de controle, ureia, creatinina e eletrólitos, se persistente.",
    },
}

for _chave, _dados in AJUSTES_TEXTOS_EXAMES_ALTERADOS.items():
    if _chave in REGRAS_EXAMES:
        REGRAS_EXAMES[_chave].update(_dados)


def chave_canonica(nome_exame):
    """
    Resolve o nome canônico do exame.

    Correção importante:
    - Primeiro tenta correspondência exata.
    - Depois faz correspondência parcial priorizando o alias mais longo.
    Assim, "Hemoglobina glicada" não cai indevidamente em "Hemoglobina".
    """
    nome_norm = normalizar_texto(nome_exame)

    candidatos = []

    for chave, aliases in ALIASES_EXAMES.items():
        formas = {normalizar_texto(chave)}
        formas.update(normalizar_texto(alias) for alias in aliases)

        for forma in formas:
            if not forma:
                continue

            candidatos.append((chave, forma))

    # 1) Exato primeiro
    for chave, forma in candidatos:
        if nome_norm == forma:
            return chave

    # 2) Parcial depois, com preferência pelo texto mais específico/longo
    parciais = []

    for chave, forma in candidatos:
        if len(forma) < 4:
            continue

        if forma in nome_norm or nome_norm in forma:
            parciais.append((len(forma), chave, forma))

    if parciais:
        parciais.sort(reverse=True)
        return parciais[0][1]

    return nome_norm



def obter_nome_exame(row):
    if not isinstance(row, dict):
        return ""

    return str(
        row.get("exame_nome")
        or row.get("nome_exame")
        or row.get("exame")
        or row.get("nome")
        or row.get("Exame")
        or ""
    ).strip()


def obter_resultado_exame(row):
    if not isinstance(row, dict):
        return None

    nome = obter_nome_exame(row)

    return extrair_numero(
        row.get("resultado")
        or row.get("Resultado")
        or row.get("valor")
        or row.get("Valor"),
        nome,
    )


def classificar_resultado(valor, regra):
    ref_min = regra.get("ref_min")
    ref_max = regra.get("ref_max")

    if ref_min is not None and valor < ref_min:
        return "baixo", "Abaixo da referência"

    if ref_max is not None and valor > ref_max:
        return "alto", "Acima da referência"

    return "normal", "Dentro da referência"


def analisar_exame(row):
    nome = obter_nome_exame(row)
    valor = obter_resultado_exame(row)

    if not nome or valor is None:
        return None

    chave = chave_canonica(nome)
    regra = REGRAS_EXAMES.get(chave)
    nome_exibicao = DISPLAY_EXAMES.get(chave, nome)

    if not regra:
        return {
            "exame": nome_exibicao,
            "chave": chave,
            "valor": valor,
            "unidade": row.get("unidade", "") if isinstance(row, dict) else "",
            "status": "sem_regra",
            "interpretacao": "Sem regra automática cadastrada",
            "possivel_condicao": "Sem regra específica para este exame.",
            "conduta": "Avaliar manualmente junto ao laudo, sintomas e contexto clínico.",
            "complementares": "",
            "severidade": 0,
        }

    regra = completar_textos_padrao(chave, dict(regra))

    # Correções defensivas para importações com decimal deslocado.
    if chave == "hemoglobina glicada" and valor is not None and valor > 20:
        while valor > 20:
            valor = valor / 10

    if chave == "urina densidade" and valor is not None and valor > 10:
        while valor > 10:
            valor = valor / 1000

    status, interpretacao = classificar_resultado(valor, regra)

    if status == "baixo":
        possivel_condicao = regra.get("baixo", "")
        conduta = regra.get("conduta_baixo", "")
        severidade = 3
    elif status == "alto":
        possivel_condicao = regra.get("alto", "")
        conduta = regra.get("conduta_alto", "")
        severidade = 3
    else:
        possivel_condicao = "Resultado dentro da referência laboratorial."
        conduta = "Manter acompanhamento evolutivo e correlacionar com sintomas, rotina alimentar e histórico."
        severidade = 0

    return {
        "exame": nome_exibicao,
        "chave": chave,
        "valor": valor,
        "unidade": regra.get("unidade", row.get("unidade", "") if isinstance(row, dict) else ""),
        "status": status,
        "interpretacao": interpretacao,
        "possivel_condicao": possivel_condicao,
        "conduta": conduta,
        "complementares": regra.get("complementares", ""),
        "severidade": severidade,
    }



def gerar_alertas_combinados(analises):
    """
    Alertas combinados entram apenas quando há alteração real fora da referência.
    """
    idx = {a.get("chave"): a for a in analises if a.get("chave")}

    def alto(chave):
        return idx.get(chave, {}).get("status") == "alto"

    def baixo(chave):
        return idx.get(chave, {}).get("status") == "baixo"

    alertas = []

    if baixo("plaquetas"):
        alertas.append({
            "titulo": "Plaquetas abaixo da referência",
            "possivel_condicao": "Trombocitopenia leve ou variação hematológica, conforme contexto.",
            "conduta": "Repetir hemograma conforme orientação e avaliar sangramentos, medicamentos e histórico clínico.",
            "severidade": 4,
        })

    if alto("urina densidade"):
        alertas.append({
            "titulo": "Densidade urinária elevada",
            "possivel_condicao": "Urina concentrada, possivelmente associada à hidratação insuficiente ou perda hídrica.",
            "conduta": "Reforçar hidratação e reavaliar urina, principalmente em rotina de treino/sudorese.",
            "severidade": 3,
        })

    if alto("colesterol total"):
        alertas.append({
            "titulo": "Colesterol total acima da referência",
            "possivel_condicao": "Dislipidemia leve ou ponto de atenção cardiovascular.",
            "conduta": "Avaliar perfil lipídico completo, fibras, qualidade das gorduras, ultraprocessados e risco global.",
            "severidade": 3,
        })

    if baixo("bilirrubina indireta"):
        alertas.append({
            "titulo": "Bilirrubina indireta abaixo da referência",
            "possivel_condicao": "Achado geralmente de menor peso isolado, mas deve ser acompanhado no painel hepático.",
            "conduta": "Correlacionar com bilirrubina total, direta, TGO, TGP e evolução.",
            "severidade": 1,
        })

    return alertas


def gerar_diagnostico_inteligente(exames):
    exames = list(exames or [])

    analises = []

    for row in exames:
        item = analisar_exame(row)
        if item:
            analises.append(item)

    alteracoes = [
        a for a in analises
        if a.get("status") in ("baixo", "alto")
    ]

    alteracoes = sorted(
        alteracoes,
        key=lambda x: (-x.get("severidade", 0), x.get("exame", ""))
    )

    alertas = gerar_alertas_combinados(analises)

    sugestoes = []

    for item in alteracoes:
        sugestoes.append({
            "exame": item["exame"],
            "interpretacao": item["interpretacao"],
            "possivel_condicao": item["possivel_condicao"],
            "conduta": item["conduta"],
            "complementares": item["complementares"],
        })

    return {
        "total_exames_analisados": len(analises),
        "total_alteracoes": len(alteracoes),
        "total_alertas_combinados": len(alertas),
        "alertas": alertas,
        "sugestoes": sugestoes,
        "analises": analises,
        "mensagem": (
            "Diagnóstico nutricional gerado como apoio técnico. "
            "A contagem de alterações considera resultados fora da referência laboratorial."
        ),
    }


def diagnostico_em_texto(exames):
    diag = gerar_diagnostico_inteligente(exames)

    linhas = []
    linhas.append("Diagnóstico nutricional")
    linhas.append(f"Exames analisados: {diag['total_exames_analisados']}")
    linhas.append(f"Alterações fora da referência: {diag['total_alteracoes']}")
    linhas.append(f"Alertas combinados: {diag['total_alertas_combinados']}")
    linhas.append("")

    if diag["alertas"]:
        linhas.append("Alertas combinados:")
        for alerta in diag["alertas"]:
            linhas.append(f"- {alerta['titulo']}: {alerta['possivel_condicao']}")
            linhas.append(f"  Conduta: {alerta['conduta']}")
        linhas.append("")

    if diag["sugestoes"]:
        linhas.append("Análise dos exames:")
        for s in diag["sugestoes"]:
            linhas.append(f"- {s['exame']}: {s['interpretacao']}")
            linhas.append(f"  Possível alteração: {s['possivel_condicao']}")
            linhas.append(f"  Conduta: {s['conduta']}")
            if s.get("complementares"):
                linhas.append(f"  Complementares: {s['complementares']}")
    else:
        linhas.append("Nenhuma alteração fora da referência laboratorial encontrada pelas regras atuais.")

    linhas.append("")
    linhas.append(diag["mensagem"])

    return "\n".join(linhas)

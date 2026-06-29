"""
Catálogo ampliado de exames, unidades, aliases e referências iniciais.

Importante:
- As referências abaixo são uma base inicial para testes, triagem e organização.
- Cada laboratório pode adotar faixas próprias.
- O profissional deve revisar e ajustar conforme laudo, método, idade, sexo e protocolo.
- O NutriSoft não faz diagnóstico; apenas compara o resultado contra a referência cadastrada.
"""

EXAMES_PADRAO = [
    # Glicêmico / metabólico
    {"nome": "Glicose", "unidade": "mg/dL", "min": 70, "max": 99, "sexo": "Todos", "aliases": ["glicose", "glicemia", "glicemia de jejum"]},
    {"nome": "Glicose pós-prandial", "unidade": "mg/dL", "min": 0, "max": 140, "sexo": "Todos", "aliases": ["glicose pos prandial", "glicose pós-prandial", "glicemia pos prandial"]},
    {"nome": "Hemoglobina glicada", "unidade": "%", "min": 4.0, "max": 5.6, "sexo": "Todos", "aliases": ["hba1c", "hemoglobina glicada", "a1c"]},
    {"nome": "Insulina", "unidade": "µUI/mL", "min": 2, "max": 25, "sexo": "Todos", "aliases": ["insulina", "insulina basal"]},
    {"nome": "Peptídeo C", "unidade": "ng/mL", "min": 0.8, "max": 3.1, "sexo": "Todos", "aliases": ["peptideo c", "peptídeo c", "c peptide"]},

    # Perfil lipídico / cardiovascular
    {"nome": "Colesterol total", "unidade": "mg/dL", "min": 0, "max": 199, "sexo": "Todos", "aliases": ["colesterol total", "colesterol"]},
    {"nome": "HDL", "unidade": "mg/dL", "min": 40, "max": 999, "sexo": "M", "aliases": ["hdl", "colesterol hdl"]},
    {"nome": "HDL", "unidade": "mg/dL", "min": 50, "max": 999, "sexo": "F", "aliases": ["hdl", "colesterol hdl"]},
    {"nome": "LDL", "unidade": "mg/dL", "min": 0, "max": 99, "sexo": "Todos", "aliases": ["ldl", "colesterol ldl"]},
    {"nome": "VLDL", "unidade": "mg/dL", "min": 0, "max": 30, "sexo": "Todos", "aliases": ["vldl", "colesterol vldl"]},
    {"nome": "Não-HDL", "unidade": "mg/dL", "min": 0, "max": 129, "sexo": "Todos", "aliases": ["nao hdl", "não hdl", "colesterol nao hdl", "colesterol não hdl"]},
    {"nome": "Triglicerídeos", "unidade": "mg/dL", "min": 0, "max": 149, "sexo": "Todos", "aliases": ["triglicerideos", "triglicerídeos", "tg"]},
    {"nome": "Apolipoproteína A1", "unidade": "mg/dL", "min": 120, "max": 180, "sexo": "Todos", "aliases": ["apoa1", "apo a1", "apolipoproteina a1"]},
    {"nome": "Apolipoproteína B", "unidade": "mg/dL", "min": 55, "max": 125, "sexo": "Todos", "aliases": ["apob", "apo b", "apolipoproteina b"]},
    {"nome": "Lipoproteína(a)", "unidade": "mg/dL", "min": 0, "max": 30, "sexo": "Todos", "aliases": ["lipoproteina a", "lipoproteína a", "lp(a)", "lpa"]},
    {"nome": "Homocisteína", "unidade": "µmol/L", "min": 5, "max": 15, "sexo": "Todos", "aliases": ["homocisteina", "homocisteína"]},

    # Vitaminas / minerais / ferro
    {"nome": "Vitamina D", "unidade": "ng/mL", "min": 20, "max": 50, "sexo": "Todos", "aliases": ["vitamina d", "vit d", "25-oh vitamina d", "25 hidroxivitamina d"]},
    {"nome": "Vitamina B12", "unidade": "pg/mL", "min": 200, "max": 900, "sexo": "Todos", "aliases": ["vitamina b12", "b12", "cobalamina"]},
    {"nome": "Ácido fólico", "unidade": "ng/mL", "min": 2.7, "max": 17, "sexo": "Todos", "aliases": ["acido folico", "ácido fólico", "folato"]},
    {"nome": "Ferritina", "unidade": "ng/mL", "min": 30, "max": 400, "sexo": "M", "aliases": ["ferritina"]},
    {"nome": "Ferritina", "unidade": "ng/mL", "min": 13, "max": 150, "sexo": "F", "aliases": ["ferritina"]},
    {"nome": "Ferro", "unidade": "µg/dL", "min": 60, "max": 170, "sexo": "Todos", "aliases": ["ferro", "ferro sérico", "ferro serico"]},
    {"nome": "Transferrina", "unidade": "mg/dL", "min": 200, "max": 360, "sexo": "Todos", "aliases": ["transferrina"]},
    {"nome": "Saturação de transferrina", "unidade": "%", "min": 20, "max": 50, "sexo": "Todos", "aliases": ["saturacao transferrina", "saturação de transferrina", "indice saturacao transferrina"]},
    {"nome": "Capacidade total de ligação do ferro", "unidade": "µg/dL", "min": 250, "max": 450, "sexo": "Todos", "aliases": ["ctlf", "tibc", "capacidade total de ligacao do ferro", "capacidade total de ligação do ferro"]},
    {"nome": "Magnésio", "unidade": "mg/dL", "min": 1.7, "max": 2.2, "sexo": "Todos", "aliases": ["magnesio", "magnésio"]},
    {"nome": "Zinco", "unidade": "µg/dL", "min": 70, "max": 120, "sexo": "Todos", "aliases": ["zinco"]},
    {"nome": "Cálcio total", "unidade": "mg/dL", "min": 8.6, "max": 10.2, "sexo": "Todos", "aliases": ["calcio", "cálcio", "calcio total", "cálcio total"]},
    {"nome": "Fósforo", "unidade": "mg/dL", "min": 2.5, "max": 4.5, "sexo": "Todos", "aliases": ["fosforo", "fósforo"]},

    # Hemograma
    {"nome": "Hemácias", "unidade": "milhões/mm³", "min": 4.6, "max": 6.2, "sexo": "M", "aliases": ["hemacias", "hemácias", "rbc"]},
    {"nome": "Hemácias", "unidade": "milhões/mm³", "min": 4.2, "max": 5.4, "sexo": "F", "aliases": ["hemacias", "hemácias", "rbc"]},
    {"nome": "Hemoglobina", "unidade": "g/dL", "min": 13.0, "max": 18.0, "sexo": "M", "aliases": ["hemoglobina", "hb"]},
    {"nome": "Hemoglobina", "unidade": "g/dL", "min": 12.0, "max": 16.0, "sexo": "F", "aliases": ["hemoglobina", "hb"]},
    {"nome": "Hematócrito", "unidade": "%", "min": 40, "max": 55, "sexo": "M", "aliases": ["hematocrito", "hematócrito", "ht"]},
    {"nome": "Hematócrito", "unidade": "%", "min": 36, "max": 48, "sexo": "F", "aliases": ["hematocrito", "hematócrito", "ht"]},
    {"nome": "VCM", "unidade": "fL", "min": 80, "max": 100, "sexo": "Todos", "aliases": ["vcm", "mcv", "volume corpuscular medio", "volume corpuscular médio"]},
    {"nome": "HCM", "unidade": "pg", "min": 27, "max": 32, "sexo": "Todos", "aliases": ["hcm", "mch", "hemoglobina corpuscular media", "hemoglobina corpuscular média"]},
    {"nome": "CHCM", "unidade": "g/dL", "min": 32, "max": 36, "sexo": "Todos", "aliases": ["chcm", "mchc"]},
    {"nome": "RDW", "unidade": "%", "min": 11.5, "max": 14.5, "sexo": "Todos", "aliases": ["rdw"]},
    {"nome": "Leucócitos", "unidade": "mil/mm³", "min": 4.5, "max": 11.0, "sexo": "Todos", "aliases": ["leucocitos", "leucócitos", "wbc"]},
    {"nome": "Neutrófilos", "unidade": "%", "min": 40, "max": 70, "sexo": "Todos", "aliases": ["neutrofilos", "neutrófilos"]},
    {"nome": "Linfócitos", "unidade": "%", "min": 20, "max": 45, "sexo": "Todos", "aliases": ["linfocitos", "linfócitos"]},
    {"nome": "Monócitos", "unidade": "%", "min": 2, "max": 10, "sexo": "Todos", "aliases": ["monocitos", "monócitos"]},
    {"nome": "Eosinófilos", "unidade": "%", "min": 1, "max": 6, "sexo": "Todos", "aliases": ["eosinofilos", "eosinófilos"]},
    {"nome": "Basófilos", "unidade": "%", "min": 0, "max": 2, "sexo": "Todos", "aliases": ["basofilos", "basófilos"]},
    {"nome": "Plaquetas", "unidade": "mil/mm³", "min": 150, "max": 450, "sexo": "Todos", "aliases": ["plaquetas", "plt"]},

    # Hepático / enzimas
    {"nome": "TGO/AST", "unidade": "U/L", "min": 10, "max": 40, "sexo": "Todos", "aliases": ["tgo", "ast", "tgo ast", "aspartato aminotransferase"]},
    {"nome": "TGP/ALT", "unidade": "U/L", "min": 7, "max": 56, "sexo": "Todos", "aliases": ["tgp", "alt", "tgp alt", "alanina aminotransferase"]},
    {"nome": "Gama GT", "unidade": "U/L", "min": 8, "max": 61, "sexo": "M", "aliases": ["gama gt", "ggt", "gama glutamil transferase"]},
    {"nome": "Gama GT", "unidade": "U/L", "min": 5, "max": 36, "sexo": "F", "aliases": ["gama gt", "ggt", "gama glutamil transferase"]},
    {"nome": "Fosfatase alcalina", "unidade": "U/L", "min": 44, "max": 147, "sexo": "Todos", "aliases": ["fosfatase alcalina", "fa", "alp"]},
    {"nome": "Bilirrubina total", "unidade": "mg/dL", "min": 0.1, "max": 1.2, "sexo": "Todos", "aliases": ["bilirrubina total", "bilirrubina"]},
    {"nome": "Bilirrubina direta", "unidade": "mg/dL", "min": 0.0, "max": 0.3, "sexo": "Todos", "aliases": ["bilirrubina direta"]},
    {"nome": "Bilirrubina indireta", "unidade": "mg/dL", "min": 0.2, "max": 0.9, "sexo": "Todos", "aliases": ["bilirrubina indireta"]},
    {"nome": "Albumina", "unidade": "g/dL", "min": 3.4, "max": 5.4, "sexo": "Todos", "aliases": ["albumina"]},
    {"nome": "Proteínas totais", "unidade": "g/dL", "min": 6.0, "max": 8.3, "sexo": "Todos", "aliases": ["proteinas totais", "proteínas totais"]},
    {"nome": "Globulina", "unidade": "g/dL", "min": 2.0, "max": 3.5, "sexo": "Todos", "aliases": ["globulina"]},
    {"nome": "LDH", "unidade": "U/L", "min": 140, "max": 280, "sexo": "Todos", "aliases": ["ldh", "desidrogenase lactica", "desidrogenase láctica"]},

    # Renal / eletrólitos
    {"nome": "Creatinina", "unidade": "mg/dL", "min": 0.74, "max": 1.35, "sexo": "M", "aliases": ["creatinina"]},
    {"nome": "Creatinina", "unidade": "mg/dL", "min": 0.59, "max": 1.04, "sexo": "F", "aliases": ["creatinina"]},
    {"nome": "Ureia", "unidade": "mg/dL", "min": 15, "max": 40, "sexo": "Todos", "aliases": ["ureia"]},
    {"nome": "Nitrogênio ureico", "unidade": "mg/dL", "min": 7, "max": 20, "sexo": "Todos", "aliases": ["bun", "nitrogenio ureico", "nitrogênio ureico"]},
    {"nome": "Ácido úrico", "unidade": "mg/dL", "min": 3.4, "max": 7.0, "sexo": "M", "aliases": ["acido urico", "ácido úrico"]},
    {"nome": "Ácido úrico", "unidade": "mg/dL", "min": 2.4, "max": 6.0, "sexo": "F", "aliases": ["acido urico", "ácido úrico"]},
    {"nome": "Sódio", "unidade": "mEq/L", "min": 135, "max": 145, "sexo": "Todos", "aliases": ["sodio", "sódio", "na"]},
    {"nome": "Potássio", "unidade": "mEq/L", "min": 3.5, "max": 5.1, "sexo": "Todos", "aliases": ["potassio", "potássio", "k"]},
    {"nome": "Cloro", "unidade": "mEq/L", "min": 98, "max": 107, "sexo": "Todos", "aliases": ["cloro", "cloreto", "cl"]},
    {"nome": "CO2 total", "unidade": "mEq/L", "min": 22, "max": 29, "sexo": "Todos", "aliases": ["co2 total", "bicarbonato", "hco3"]},
    {"nome": "TFG estimada", "unidade": "mL/min/1.73m²", "min": 60, "max": 999, "sexo": "Todos", "aliases": ["tfg", "egfr", "filtracao glomerular", "filtração glomerular"]},

    # Tireoidiano
    {"nome": "TSH", "unidade": "mUI/L", "min": 0.4, "max": 4.0, "sexo": "Todos", "aliases": ["tsh"]},
    {"nome": "T4 livre", "unidade": "ng/dL", "min": 0.8, "max": 1.8, "sexo": "Todos", "aliases": ["t4 livre", "t4l", "ft4"]},
    {"nome": "T3 livre", "unidade": "pg/mL", "min": 2.3, "max": 4.2, "sexo": "Todos", "aliases": ["t3 livre", "t3l", "ft3"]},
    {"nome": "T4 total", "unidade": "µg/dL", "min": 5.0, "max": 12.0, "sexo": "Todos", "aliases": ["t4 total"]},
    {"nome": "T3 total", "unidade": "ng/dL", "min": 80, "max": 180, "sexo": "Todos", "aliases": ["t3 total"]},
    {"nome": "Anti-TPO", "unidade": "UI/mL", "min": 0, "max": 35, "sexo": "Todos", "aliases": ["anti tpo", "antitpo", "anticorpo anti tpo"]},
    {"nome": "Anti-tireoglobulina", "unidade": "UI/mL", "min": 0, "max": 40, "sexo": "Todos", "aliases": ["anti tireoglobulina", "antitireoglobulina", "anti tg"]},

    # Inflamatório / muscular
    {"nome": "PCR", "unidade": "mg/L", "min": 0, "max": 5, "sexo": "Todos", "aliases": ["pcr", "proteina c reativa", "proteína c reativa"]},
    {"nome": "PCR ultrassensível", "unidade": "mg/L", "min": 0, "max": 3, "sexo": "Todos", "aliases": ["pcr us", "pcr ultra", "pcr ultrassensivel", "pcr ultrassensível", "hs-crp"]},
    {"nome": "VHS", "unidade": "mm/h", "min": 0, "max": 20, "sexo": "Todos", "aliases": ["vhs", "velocidade hemossedimentacao", "velocidade de hemossedimentação"]},
    {"nome": "CK", "unidade": "U/L", "min": 30, "max": 200, "sexo": "Todos", "aliases": ["ck", "cpk", "creatinoquinase", "creatina quinase"]},

    # Hormonal / nutricional complementar
    {"nome": "Cortisol manhã", "unidade": "µg/dL", "min": 6.2, "max": 19.4, "sexo": "Todos", "aliases": ["cortisol manha", "cortisol manhã", "cortisol basal"]},
    {"nome": "Testosterona total", "unidade": "ng/dL", "min": 300, "max": 1000, "sexo": "M", "aliases": ["testosterona total"]},
    {"nome": "Testosterona total", "unidade": "ng/dL", "min": 15, "max": 70, "sexo": "F", "aliases": ["testosterona total"]},
    {"nome": "SHBG", "unidade": "nmol/L", "min": 10, "max": 57, "sexo": "M", "aliases": ["shbg", "globulina ligadora de hormônios sexuais"]},
    {"nome": "SHBG", "unidade": "nmol/L", "min": 18, "max": 144, "sexo": "F", "aliases": ["shbg", "globulina ligadora de hormônios sexuais"]},
    {"nome": "DHEA-S", "unidade": "µg/dL", "min": 80, "max": 560, "sexo": "Todos", "aliases": ["dhea-s", "dheas", "sulfato de dhea"]},

    # Urina / metabólico complementar
    {"nome": "Microalbuminúria", "unidade": "mg/g", "min": 0, "max": 30, "sexo": "Todos", "aliases": ["microalbuminuria", "microalbuminúria", "albumina creatinina urina"]},
    {"nome": "Relação albumina/creatinina", "unidade": "mg/g", "min": 0, "max": 30, "sexo": "Todos", "aliases": ["relacao albumina creatinina", "relação albumina creatinina", "acr"]},
]

EXAMES_COMUNS = [""] + sorted({item["nome"] for item in EXAMES_PADRAO}) + ["Outro"]
UNIDADES_COMUNS = [""] + sorted({item["unidade"] for item in EXAMES_PADRAO}) + ["Outro"]

FONTES_REFERENCIA = {
    "geral": "Merck Manual Professional - Laboratory Reference Ranges; MedlinePlus/NLM - orientação de interpretação laboratorial",
    "lipidico": "MedlinePlus/NLM - Cholesterol Levels; MedlinePlus Medical Encyclopedia - Lipid profile test",
    "hemograma": "MedlinePlus Medical Encyclopedia - CBC blood test; MedlinePlus/NLM - Complete Blood Count",
    "metabolico": "MedlinePlus Medical Encyclopedia - Comprehensive metabolic panel; MedlinePlus/NLM - Comprehensive Metabolic Panel",
    "tireoide": "MedlinePlus Medical Encyclopedia - TSH test; MedlinePlus/NLM - Thyroxine (T4) Test",
    "ferritina": "UCSF Health - Ferritin blood test; Cleveland Clinic - Ferritin Test",
    "vitamina_d": "Mayo Clinic Laboratories - 25-Hydroxyvitamin D2 and D3 Serum; Mayo Clinic News Network - Vitamin D toxicity study",
}


def _fonte_por_exame(nome: str) -> str:
    nome_norm = str(nome or "").lower()

    if any(t in nome_norm for t in ["colesterol", "hdl", "ldl", "vldl", "triglicer", "apolipoproteína", "apolipoproteina", "lipoproteína", "lipoproteina"]):
        return FONTES_REFERENCIA["lipidico"]

    if any(t in nome_norm for t in ["hemácias", "hemacias", "hemoglobina", "hematócrito", "hematocrito", "vcm", "hcm", "chcm", "rdw", "leucócitos", "leucocitos", "neutrófilos", "linfócitos", "monócitos", "eosinófilos", "basófilos", "plaquetas"]):
        return FONTES_REFERENCIA["hemograma"]

    if any(t in nome_norm for t in ["glicose", "sódio", "sodio", "potássio", "potassio", "cloro", "creatinina", "ureia", "albumina", "proteínas", "proteinas", "bilirrubina", "tgo", "tgp", "ast", "alt", "fosfatase", "gama gt", "ácido úrico", "acido urico"]):
        return FONTES_REFERENCIA["metabolico"]

    if any(t in nome_norm for t in ["tsh", "t4", "t3", "anti-tpo", "anti tireoglobulina", "anti-tireoglobulina"]):
        return FONTES_REFERENCIA["tireoide"]

    if "ferritina" in nome_norm:
        return FONTES_REFERENCIA["ferritina"]

    if "vitamina d" in nome_norm:
        return FONTES_REFERENCIA["vitamina_d"]

    return FONTES_REFERENCIA["geral"]


def referencias_para_cadastro() -> list[dict]:
    linhas = []
    for item in EXAMES_PADRAO:
        fonte = item.get("fonte") or _fonte_por_exame(item["nome"])
        linhas.append({
            "nome_exame": item["nome"],
            "sexo": item["sexo"],
            "idade_min": "18",
            "idade_max": "120",
            "valor_min": str(item["min"]),
            "valor_max": str(item["max"]),
            "unidade": item["unidade"],
            "fonte_referencia": fonte,
            "observacoes": (
                "Referência inicial adulta, rastreável e editável. "
                "Confirmar com o intervalo do laboratório, método, unidade, idade, sexo, gestação, altitude, medicações e contexto clínico."
            ),
        })
    return linhas


def aliases_para_cadastro() -> list[dict]:
    vistos = set()
    linhas = []
    for item in EXAMES_PADRAO:
        # Inclui o próprio nome do exame como alias para padronização.
        aliases = [item["nome"]] + item.get("aliases", [])
        for alias in aliases:
            chave = (alias.lower(), item["nome"])
            if chave not in vistos:
                vistos.add(chave)
                linhas.append({"alias": alias, "nome_padronizado": item["nome"]})
    return linhas


def cobertura_catalogo() -> dict:
    exames = sorted({item["nome"] for item in EXAMES_PADRAO})
    refs = referencias_para_cadastro()
    nomes_com_ref = {r["nome_exame"] for r in refs}

    sem_ref = [nome for nome in exames if nome not in nomes_com_ref]

    return {
        "total_exames": len(exames),
        "total_referencias": len(refs),
        "exames_sem_referencia": sem_ref,
        "cobertura_percentual": 100.0 if not exames else round((len(exames) - len(sem_ref)) / len(exames) * 100, 1),
    }

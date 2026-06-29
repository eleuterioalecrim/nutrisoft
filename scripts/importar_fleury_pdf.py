from pathlib import Path
from datetime import datetime
import argparse
import csv
import re
import unicodedata
import sys

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None


APP_DIR = Path(__file__).resolve().parents[1]
DATA_FLET = APP_DIR / "data_flet"

COL_PACIENTES = [
    "paciente_id", "data_cadastro", "nome", "data_nascimento", "idade",
    "sexo", "telefone", "email", "profissao", "horario_trabalho", "observacoes",
]

COL_EXAMES = [
    "exame_id", "paciente_id", "data_exame", "nome_exame",
    "resultado", "unidade", "observacoes",
]

COL_ANALISE = [
    "analise_id", "paciente_id", "data_exame", "nome_exame", "nome_padronizado",
    "resultado", "unidade", "valor_min", "valor_max", "status",
    "mensagem", "fonte_referencia",
]

COL_REFERENCIAS = [
    "id", "nome", "nome_exame", "grupo", "sexo", "idade_min", "idade_max",
    "valor_min", "valor_max", "unidade", "referencia", "referencia_texto",
    "fonte", "fonte_referencia", "observacoes", "status",
]

COL_ALIAS = ["alias", "nome_padronizado"]


def normalizar(txt):
    txt = str(txt or "").strip()
    txt = unicodedata.normalize("NFKD", txt)
    txt = txt.encode("ascii", "ignore").decode("ascii")
    txt = re.sub(r"\s+", " ", txt)
    return txt.lower().strip()


def slug(txt):
    txt = normalizar(txt)
    txt = re.sub(r"[^a-z0-9]+", "_", txt).strip("_")
    return txt


def parse_num(valor):
    valor = str(valor or "").strip()
    valor = re.sub(r"[^0-9,.\-]", "", valor)

    if not valor:
        return None

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")
    else:
        partes = valor.split(".")
        if len(partes) == 2 and len(partes[1]) == 3 and len(partes[0]) <= 3:
            valor = "".join(partes)

    try:
        return float(valor)
    except Exception:
        return None


def resultado_para_csv(valor):
    n = parse_num(valor)

    if n is None:
        return str(valor or "").strip()

    if float(n).is_integer():
        return str(int(n))

    return str(n).replace(".", ".")


def status_resultado(valor, valor_min, valor_max):
    v = parse_num(valor)
    vmin = parse_num(valor_min)
    vmax = parse_num(valor_max)

    if v is None:
        return "Sem análise"

    if vmin is not None and v < vmin:
        return "Baixo"

    if vmax is not None and v > vmax:
        return "Alto"

    return "Normal"


def ler_csv(path, colunas):
    DATA_FLET.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=colunas)
            w.writeheader()
        return []

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except UnicodeDecodeError:
        with path.open("r", encoding="latin-1", newline="") as f:
            return list(csv.DictReader(f))


def escrever_csv(path, colunas, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colunas)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in colunas})


def upsert_rows(path, colunas, rows_novas, chaves):
    rows = ler_csv(path, colunas)

    def key(row):
        return tuple(normalizar(row.get(c, "")) for c in chaves)

    mapa = {key(r): dict(r) for r in rows}

    for nova in rows_novas:
        k = key(nova)
        base = mapa.get(k, {})
        base.update(nova)
        mapa[k] = base

    escrever_csv(path, colunas, list(mapa.values()))


def proximo_id(rows, campo):
    maior = 0

    for r in rows:
        try:
            maior = max(maior, int(str(r.get(campo, "")).strip()))
        except Exception:
            pass

    return maior + 1


def extrair_texto_pdf(pdf_path):
    if PdfReader is None:
        raise SystemExit("Instale o pypdf: python3 -m pip install --user --break-system-packages pypdf")

    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extrair_cabecalho(texto):
    ficha = ""
    data_laudo = ""
    nome = ""
    nascimento = ""

    m = re.search(r"Ficha:\s*([0-9]+)", texto, re.I)
    if m:
        ficha = m.group(1).strip()

    m = re.search(r"Data:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})", texto, re.I)
    if m:
        data_laudo = m.group(1).strip()

    m = re.search(r"Cliente:\s*(.+)", texto, re.I)
    if m:
        nome = m.group(1).strip()

    m = re.search(r"Data de Nascimento:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})", texto, re.I)
    if m:
        nascimento = m.group(1).strip()

    return {
        "ficha": ficha,
        "data_laudo": data_laudo,
        "nome": nome,
        "nascimento": nascimento,
    }


def data_br_para_iso(data_br):
    data_br = str(data_br or "").strip()

    if not data_br:
        return ""

    if "-" in data_br:
        return data_br

    try:
        return datetime.strptime(data_br, "%d/%m/%Y").strftime("%Y-%m-%d")
    except Exception:
        return data_br


def idade_por_nascimento(data_br):
    try:
        nasc = datetime.strptime(data_br, "%d/%m/%Y")
        hoje = datetime.now()
        return str(hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day)))
    except Exception:
        return ""




def encontrar_paciente_sem_criar(cabecalho, paciente_id_forcado=None):
    path = DATA_FLET / "pacientes.csv"
    rows = ler_csv(path, COL_PACIENTES)

    if paciente_id_forcado:
        for r in rows:
            if str(r.get("paciente_id", "")).strip() == str(paciente_id_forcado):
                return str(paciente_id_forcado)
        return str(paciente_id_forcado)

    nome_pdf = cabecalho.get("nome", "")
    nome_norm = normalizar(nome_pdf)

    for r in rows:
        if normalizar(r.get("nome", "")) == nome_norm:
            return str(r.get("paciente_id", "")).strip()

    for r in rows:
        if nome_norm and nome_norm in normalizar(r.get("nome", "")):
            return str(r.get("paciente_id", "")).strip()

    return ""


def encontrar_ou_criar_paciente(cabecalho, paciente_id_forcado=None):
    path = DATA_FLET / "pacientes.csv"
    rows = ler_csv(path, COL_PACIENTES)

    if paciente_id_forcado:
        for r in rows:
            if str(r.get("paciente_id", "")).strip() == str(paciente_id_forcado):
                return str(paciente_id_forcado)

    nome_pdf = cabecalho.get("nome", "")
    nome_norm = normalizar(nome_pdf)

    for r in rows:
        if normalizar(r.get("nome", "")) == nome_norm:
            return str(r.get("paciente_id", "")).strip()

    for r in rows:
        if nome_norm and nome_norm in normalizar(r.get("nome", "")):
            return str(r.get("paciente_id", "")).strip()

    novo_id_num = 1

    ids = []
    for r in rows:
        try:
            ids.append(int(str(r.get("paciente_id", "")).strip()))
        except Exception:
            pass

    if ids:
        novo_id_num = max(ids) + 1

    novo_id = str(novo_id_num).zfill(4)

    rows.append({
        "paciente_id": novo_id,
        "data_cadastro": datetime.now().strftime("%Y-%m-%d"),
        "nome": nome_pdf.title(),
        "data_nascimento": cabecalho.get("nascimento", ""),
        "idade": idade_por_nascimento(cabecalho.get("nascimento", "")),
        "sexo": "",
        "telefone": "",
        "email": "",
        "profissao": "",
        "horario_trabalho": "",
        "observacoes": f"Criado automaticamente na importação da ficha Fleury {cabecalho.get('ficha', '')}",
    })

    escrever_csv(path, COL_PACIENTES, rows)
    return novo_id


def add_def(catalogo, nome, grupo, unidade, vmin, vmax, referencia, regex):
    catalogo.append({
        "nome": nome,
        "grupo": grupo,
        "unidade": unidade,
        "valor_min": str(vmin or ""),
        "valor_max": str(vmax or ""),
        "referencia": referencia,
        "regex": regex,
        "fonte": "Fleury/F. Mattoso - ficha importada",
    })


def montar_catalogo():
    c = []

    add_def(c, "TTPA - relação paciente/normal", "Coagulação", "relação", "0.91", "1.20", "0,91 a 1,20", r"RELACAO PACIENTE/NORMAL:\s*([0-9,.]+)\s+0,91\s+a\s+1,20")
    add_def(c, "Tempo de protrombina", "Coagulação", "segundos", "10.1", "12.8", "10,1 a 12,8 segundos", r"TEMPO DE PROTROMBINA.*?\nRESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*segundos")
    add_def(c, "INR", "Coagulação", "INR", "0.9", "1.1", "0,9 a 1,1", r"INR:\s*([0-9,.]+)\s+0,9\s+a\s+1,1")

    add_def(c, "Hemoglobina glicada", "Metabolismo glicídico", "%", "", "5.69", "Menor que 5,7%: baixo risco; 5,7 a 6,4%: risco aumentado; >=6,5%: consistente com diabetes", r"HEMOGLOBINA GLICADA.*?RESULTADO\s*\n([0-9,.]+)\s*%")
    add_def(c, "Glicemia média estimada", "Metabolismo glicídico", "mg/dL", "", "", "Valor calculado a partir da hemoglobina glicada", r"glicemia média estimada\s*\nde\s*([0-9,.]+)\s*mg/dL")
    add_def(c, "Glicose", "Metabolismo glicídico", "mg/dL", "70", "99", "70 a 99 mg/dL", r"GLICOSE, plasma.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mg/dL")
    add_def(c, "Insulina", "Metabolismo glicídico", "mU/L", "2", "13", "Insulina em jejum: 2 a 13 mU/L", r"INSULINA.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mU/L")
    add_def(c, "HOMA-IR", "Metabolismo glicídico", "índice", "0", "2.71", "Valores acima de 2,71 foram relacionados com resistência à insulina em estudo populacional brasileiro", r"Cálculo do HOMA-IR:\s*([0-9,.]+)")

    add_def(c, "Eritrócitos", "Hemograma", "milhões/mm3", "4.32", "5.67", "Masculino adulto: 4,32 a 5,67 milhões/mm3", r"ERITRÓCITOS\s*:\s*([0-9,.]+)\s*milhões/mm3")
    add_def(c, "Hemoglobina", "Hemograma", "g/dL", "13.3", "16.5", "Masculino adulto: 13,3 a 16,5 g/dL", r"HEMOGLOBINA\s*:\s*([0-9,.]+)\s*g/dL")
    add_def(c, "Hematócrito", "Hemograma", "%", "39.2", "49.0", "Masculino adulto: 39,2 a 49,0%", r"HEMATÓCRITO\s*:\s*([0-9,.]+)\s*%")
    add_def(c, "HCM", "Hemograma", "pg", "27.7", "32.7", "27,7 a 32,7 pg", r"HEMOGLOBINA CORPUSCULAR MÉDIA\s*:\s*([0-9,.]+)\s*pg")
    add_def(c, "VCM", "Hemograma", "fL", "81.7", "95.3", "81,7 a 95,3 fL", r"VOLUME CORPUSCULAR MÉDIO\s*:\s*([0-9,.]+)\s*fL")
    add_def(c, "CHCM", "Hemograma", "g/dL", "32.4", "36.0", "32,4 a 36,0 g/dL", r"CORPUSCULAR MÉDIA:\s*([0-9,.]+)\s*g/dL")
    add_def(c, "RDW", "Hemograma", "%", "11.8", "14.1", "11,8 a 14,1%", r"VOLUME ERITROCITÁRIO \(RDW\):\s*([0-9,.]+)\s*%")

    add_def(c, "Leucócitos", "Hemograma", "/mm3", "3650", "8120", "3.650 a 8.120/mm3", r"LEUCÓCITOS\s+([0-9.]+)\s+3\.650\s+a\s+8\.120")
    add_def(c, "Neutrófilos", "Hemograma", "/mm3", "1590", "4770", "1.590 a 4.770/mm3", r"Neutrófilos\s*:\s*[0-9,.]+\s+([0-9.]+)\s+1\.590\s+a\s+4\.770")
    add_def(c, "Eosinófilos", "Hemograma", "/mm3", "34", "420", "34 a 420/mm3", r"Eosinófilos\s*:\s*[0-9,.]+\s+([0-9.]+)\s+34\s+a\s+420")
    add_def(c, "Basófilos", "Hemograma", "/mm3", "10", "80", "10 a 80/mm3", r"Basófilos\s*:\s*[0-9,.]+\s+([0-9.]+)\s+10\s+a\s+80")
    add_def(c, "Linfócitos", "Hemograma", "/mm3", "1120", "2950", "1.120 a 2.950/mm3", r"Linfócitos\s*:\s*[0-9,.]+\s+([0-9.]+)\s+1\.120\s+a\s+2\.950")
    add_def(c, "Monócitos", "Hemograma", "/mm3", "260", "730", "260 a 730/mm3", r"Monócitos\s*:\s*[0-9,.]+\s+([0-9.]+)\s+260\s+a\s+730")
    add_def(c, "Plaquetas", "Hemograma", "/mm3", "151000", "304000", "151.000 a 304.000/mm3", r"TOTAL DE PLAQUETAS:\s*([0-9.]+)\/mm3")
    add_def(c, "Volume plaquetário médio", "Hemograma", "fL", "9.2", "12.6", "9,2 a 12,6 fL", r"VOLUME PLAQUETÁRIO MÉDIO:\s*([0-9,.]+)\s*fL")

    add_def(c, "VHS", "Inflamação", "mm", "2", "28", "Masculino 18 a 65 anos: 2 a 28 mm na primeira hora", r"PRIMEIRA HORA\s*:\s*([0-9,.]+)\s*mm")
    add_def(c, "Proteína C-Reativa ultrassensível", "Inflamação / Cardiovascular", "mg/dL", "0", "0.3", "Risco cardiovascular: <0,1 baixo; 0,1 a 0,3 intermediário; >0,3 alto", r"PROTEINA C-REATIVA.*?RESULTADO\s*\n([0-9,.]+)\s*mg/dL")

    add_def(c, "Ácido fólico", "Vitaminas", "ng/mL", "3.9", "", "Superior a 3,9 ng/mL", r"ACIDO FOLICO.*?RESULTADO\s+VALOR DE REFERÊNCIA\s*\n([0-9,.]+)\s*ng/mL")
    add_def(c, "Vitamina B12", "Vitaminas", "ng/L", "300", "", "Normal: maior que 300 ng/L; limítrofe: 190 a 300; deficiente: menor que 190", r"VITAMINA B-12.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*ng/L")
    add_def(c, "25-OH Vitamina D", "Vitaminas", "ng/mL", "20", "100", "População saudável até 60 anos: acima de 20 ng/mL; deficiência <20; risco de toxicidade >100", r"25 HIDROXI-VITAMINA D.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*ng/mL")

    add_def(c, "Ferro", "Metabolismo do ferro", "mcg/dL", "65", "175", "Acima de 12 anos: 65 a 175 mcg/dL", r"Ferro\s*:\s*([0-9,.]+)\s*mcg/dL")
    add_def(c, "Ferritina", "Metabolismo do ferro", "microg/L", "26", "446", "Sexo masculino: 26 a 446 microg/L", r"FERRITINA.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*microg/L")
    add_def(c, "Saturação da transferrina", "Metabolismo do ferro", "%", "20", "50", "20 a 50%", r"Saturação da transferrina\s*:\s*([0-9,.]+)\s*%")

    add_def(c, "AST/TGO", "Função hepática", "U/L", "0", "50", "Masculino maior de 2 anos: até 50 U/L", r"ASPARTATO AMINO TRANSFERASE.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*U/L")
    add_def(c, "ALT/TGP", "Função hepática", "U/L", "0", "50", "Masculino maior de 1 ano: até 50 U/L", r"ALANINA AMINO TRANSFERASE.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*U/L")
    add_def(c, "Fosfatase alcalina", "Função hepática", "U/L", "40", "129", "Adultos: 40 a 129 U/L", r"FOSFATASE ALCALINA.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*U/L")
    add_def(c, "Gama GT", "Função hepática", "U/L", "12", "73", "Masculino: 12 a 73 U/L", r"GAMA GLUTAMIL TRANSFERASE.*?RESULTADO\s+VALOR DE REFERÊNCIA\s*\n([0-9,.]+)\s*U/L")
    add_def(c, "Bilirrubina direta", "Função hepática", "mg/dL", "0", "0.30", "0,00 a 0,30 mg/dL", r"DIRETA\s*:\s*([0-9,.]+)\s*mg/dL")
    add_def(c, "Bilirrubina indireta", "Função hepática", "mg/dL", "0.20", "0.80", "0,20 a 0,80 mg/dL", r"INDIRETA:\s*([0-9,.]+)\s*mg/dL")
    add_def(c, "Bilirrubina total", "Função hepática", "mg/dL", "0.20", "1.10", "0,20 a 1,10 mg/dL", r"TOTAL\s*:\s*([0-9,.]+)\s*mg/dL")

    add_def(c, "Proteína total", "Proteínas séricas", "g/dL", "6.5", "8.1", "6,5 a 8,1 g/dL", r"PROTEINA TOTAL:\s*([0-9,.]+)\s*g/dL")
    add_def(c, "Albumina", "Proteínas séricas", "g/dL", "3.5", "5.2", "3,5 a 5,2 g/dL", r"ALBUMINA\s*:\s*([0-9,.]+)\s*g/dL")
    add_def(c, "Globulinas", "Proteínas séricas", "g/dL", "1.7", "3.5", "1,7 a 3,5 g/dL", r"GLOBULINAS\s*:\s*([0-9,.]+)\s*g/dL")
    add_def(c, "Relação albumina/globulinas", "Proteínas séricas", "relação", "0.9", "2.0", "0,9 a 2,0", r"ALBUMINA/GLOBULINAS:\s*([0-9,.]+)")

    add_def(c, "Creatinina", "Função renal", "mg/dL", "0.70", "1.30", "Acima de 12 anos: 0,70 a 1,30 mg/dL", r"CREATININA.*?RESULTADO\s+VALOR DE REFERÊNCIA\s*\n([0-9,.]+)\s*mg/dL")
    add_def(c, "TFG CKD-EPI 2021", "Função renal", "mL/min/1,73m2", "60", "", "Superior a 60 mL/min/1,73m2", r"CKD-EPI 2021\s*:\s*([0-9,.]+)\s+superior\s+a\s+60")
    add_def(c, "Ureia", "Função renal", "mg/dL", "10", "50", "10 a 50 mg/dL", r"UREIA.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mg/dL")

    add_def(c, "Sódio", "Eletrólitos", "mEq/L", "136", "145", "136 a 145 mEq/L", r"SODIO.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mEq/L")
    add_def(c, "Potássio", "Eletrólitos", "mEq/L", "3.5", "5.1", "A partir de 1 ano: 3,5 a 5,1 mEq/L", r"POTASSIO.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mEq/L")
    add_def(c, "Cálcio ionizado", "Eletrólitos", "mmol/L", "1.11", "1.40", "1,11 a 1,40 mmol/L", r"CALCIO IONIZADO.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mmol/L")
    add_def(c, "Magnésio", "Eletrólitos", "mg/dL", "1.6", "2.6", "Acima de 20 anos: 1,6 a 2,6 mg/dL", r"MAGNESIO.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mg/dL")

    add_def(c, "Colesterol total", "Perfil lipídico", "mg/dL", "0", "189.99", "Desejável: menor que 190 mg/dL", r"COLESTEROL TOTAL.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mg/dL")
    add_def(c, "Triglicerídeos", "Perfil lipídico", "mg/dL", "0", "150", "Com jejum: desejável <150 mg/dL; sem jejum: desejável <175 mg/dL", r"TRIGLICERIDES.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mg/dL")
    add_def(c, "HDL colesterol", "Perfil lipídico", "mg/dL", "40", "", "Desejável: maior que 40 mg/dL", r"HDL-COLESTEROL.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mg/dL")
    add_def(c, "VLDL colesterol", "Perfil lipídico", "mg/dL", "0", "30", "Com jejum: desejável <30 mg/dL; sem jejum: desejável <35 mg/dL", r"VLDL-COLESTEROL.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mg/dL")
    add_def(c, "LDL colesterol", "Perfil lipídico", "mg/dL", "0", "129", "Ótimo <100; desejável 100 a 129; limítrofe 130 a 159; alto 160 a 189; muito alto >=190", r"(?<!V)LDL-COLESTEROL.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mg/dL")
    add_def(c, "Colesterol não-HDL", "Perfil lipídico", "mg/dL", "0", "159", "Ótimo <130; desejável 130 a 159; alto 160 a 189; muito alto >=190", r"NÃO-HDL-COLESTEROL.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mg/dL")

    add_def(c, "TSH", "Tireoide", "mUI/L", "0.45", "4.5", "20 a 59 anos: 0,45 a 4,5 mUI/L", r"HORMONIO TIROESTIMULANTE.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*mUI/L")
    add_def(c, "T4 livre", "Tireoide", "ng/dL", "0.9", "1.7", "Acima de 20 anos: 0,9 a 1,7 ng/dL", r"TIROXINA \(T4\) LIVRE.*?RESULTADO\s+VALORES DE REFERÊNCIA\s*\n([0-9,.]+)\s*ng/dL")

    add_def(c, "Urina pH", "Urina tipo I", "pH", "5.0", "8.0", "5,0 a 8,0", r"pH\s*:\s*([0-9,.]+)\s+de\s+5,0\s+a\s+8,0")
    add_def(c, "Urina densidade", "Urina tipo I", "densidade", "1,010", "1,030", "1,010 a 1,030", r"DENSIDADE\s*:\s*([0-9,.]+)\s+de\s+1,010\s+a\s+1,030")

    return c


ALIASES = {
    "TTPA": "TTPA - relação paciente/normal",
    "TEMPO DE TROMBOPLASTINA PARCIAL ATIVADA": "TTPA - relação paciente/normal",
    "TP": "Tempo de protrombina",
    "TEMPO DE PROTROMBINA": "Tempo de protrombina",
    "A1C": "Hemoglobina glicada",
    "HbA1c": "Hemoglobina glicada",
    "HEMOGLOBINA GLICADA (A1C)": "Hemoglobina glicada",
    "GLICOSE, plasma": "Glicose",
    "HEMÁCIAS": "Eritrócitos",
    "ERITRÓCITOS": "Eritrócitos",
    "HEMOGLOBINA CORPUSCULAR MÉDIA": "HCM",
    "VOLUME CORPUSCULAR MÉDIO": "VCM",
    "CONCENTRAÇÃO DE HEMOGLOBINA CORPUSCULAR MÉDIA": "CHCM",
    "COEFICIENTE DE VARIAÇÃO DO VOLUME ERITROCITÁRIO": "RDW",
    "TOTAL DE PLAQUETAS": "Plaquetas",
    "VPM": "Volume plaquetário médio",
    "VHS": "VHS",
    "HEMOSSEDIMENTACAO": "VHS",
    "ACIDO FOLICO": "Ácido fólico",
    "ÁCIDO FÓLICO": "Ácido fólico",
    "TGO": "AST/TGO",
    "AST": "AST/TGO",
    "TGP": "ALT/TGP",
    "ALT": "ALT/TGP",
    "GAMA-GT": "Gama GT",
    "GGT": "Gama GT",
    "CALCIO IONIZADO": "Cálcio ionizado",
    "CREATININA": "Creatinina",
    "FERRITINA": "Ferritina",
    "FERRO": "Ferro",
    "SATURAÇÃO DA TRANSFERRINA": "Saturação da transferrina",
    "COLESTEROL TOTAL": "Colesterol total",
    "HDL": "HDL colesterol",
    "HDL-COLESTEROL": "HDL colesterol",
    "LDL": "LDL colesterol",
    "LDL-COLESTEROL": "LDL colesterol",
    "VLDL": "VLDL colesterol",
    "VLDL-COLESTEROL": "VLDL colesterol",
    "NÃO-HDL-COLESTEROL": "Colesterol não-HDL",
    "TRIGLICERIDES": "Triglicerídeos",
    "PCR": "Proteína C-Reativa ultrassensível",
    "PROTEINA C-REATIVA": "Proteína C-Reativa ultrassensível",
    "TSH": "TSH",
    "HORMONIO TIROESTIMULANTE": "TSH",
    "T4 LIVRE": "T4 livre",
    "TIROXINA (T4) LIVRE": "T4 livre",
    "VITAMINA B-12": "Vitamina B12",
    "VITAMINA B12": "Vitamina B12",
    "25 HIDROXI-VITAMINA D": "25-OH Vitamina D",
    "VITAMINA D": "25-OH Vitamina D",
}


def atualizar_catalogo(catalogo):
    ref_rows = []
    alias_rows = []

    for e in catalogo:
        ref_rows.append({
            "id": slug(e["nome"]),
            "nome": e["nome"],
            "nome_exame": e["nome"],
            "grupo": e["grupo"],
            "sexo": "Todos",
            "idade_min": "",
            "idade_max": "",
            "valor_min": e["valor_min"],
            "valor_max": e["valor_max"],
            "unidade": e["unidade"],
            "referencia": e["referencia"],
            "referencia_texto": e["referencia"],
            "fonte": e["fonte"],
            "fonte_referencia": e["fonte"],
            "observacoes": "Incluído/atualizado pelo importador Fleury",
            "status": "Completa",
        })

    for alias, padrao in ALIASES.items():
        alias_rows.append({"alias": alias, "nome_padronizado": padrao})

    upsert_rows(DATA_FLET / "referencias_exames.csv", COL_REFERENCIAS, ref_rows, ["nome_exame", "unidade"])
    upsert_rows(DATA_FLET / "alias_exames.csv", COL_ALIAS, alias_rows, ["alias"])


def extrair_resultados(texto, catalogo):
    resultados = []

    for e in catalogo:
        m = re.search(e["regex"], texto, re.S | re.I)

        if not m:
            continue

        resultado_original = m.group(1).strip()
        resultado_csv = resultado_para_csv(resultado_original)
        status = status_resultado(resultado_original, e["valor_min"], e["valor_max"])

        resultados.append({
            "nome_exame": e["nome"],
            "nome_padronizado": e["nome"],
            "grupo": e["grupo"],
            "resultado": resultado_csv,
            "resultado_original": resultado_original,
            "unidade": e["unidade"],
            "valor_min": e["valor_min"],
            "valor_max": e["valor_max"],
            "status": status,
            "referencia": e["referencia"],
            "fonte": e["fonte"],
        })

    return resultados


def importar_resultados(paciente_id, data_exame, resultados, ficha):
    path_exames = DATA_FLET / "exames.csv"
    path_analise = DATA_FLET / "analise_exames.csv"

    exames_existentes = ler_csv(path_exames, COL_EXAMES)
    analises_existentes = ler_csv(path_analise, COL_ANALISE)

    prox_exame_id = proximo_id(exames_existentes, "exame_id")
    prox_analise_id = proximo_id(analises_existentes, "analise_id")

    exames_rows = []
    analise_rows = []

    for r in resultados:
        exames_rows.append({
            "exame_id": str(prox_exame_id).zfill(4),
            "paciente_id": paciente_id,
            "data_exame": data_exame,
            "nome_exame": r["nome_exame"],
            "resultado": r["resultado"],
            "unidade": r["unidade"],
            "observacoes": f"Importado do PDF Fleury/F. Mattoso ficha {ficha}",
        })
        prox_exame_id += 1

        mensagem = f'{r["nome_exame"]}: {r["resultado"]} {r["unidade"]} - {r["status"]}. Referência: {r["referencia"]}'

        analise_rows.append({
            "analise_id": str(prox_analise_id),
            "paciente_id": paciente_id,
            "data_exame": data_exame,
            "nome_exame": r["nome_exame"],
            "nome_padronizado": r["nome_padronizado"],
            "resultado": r["resultado"],
            "unidade": r["unidade"],
            "valor_min": r["valor_min"],
            "valor_max": r["valor_max"],
            "status": r["status"],
            "mensagem": mensagem,
            "fonte_referencia": r["fonte"],
        })
        prox_analise_id += 1

    upsert_rows(path_exames, COL_EXAMES, exames_rows, ["paciente_id", "data_exame", "nome_exame"])
    upsert_rows(path_analise, COL_ANALISE, analise_rows, ["paciente_id", "data_exame", "nome_exame"])


def main():
    parser = argparse.ArgumentParser(description="Importa PDF de resultados Fleury/F. Mattoso para data_flet.")
    parser.add_argument("pdf", help="Caminho do PDF do laudo")
    parser.add_argument("--paciente-id", default="", help="Força o paciente_id caso deseje")
    parser.add_argument("--dry-run", action="store_true", help="Apenas mostra o que seria importado")
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()

    if not pdf_path.exists():
        raise SystemExit(f"PDF não encontrado: {pdf_path}")

    texto = extrair_texto_pdf(pdf_path)
    cabecalho = extrair_cabecalho(texto)
    catalogo = montar_catalogo()
    resultados = extrair_resultados(texto, catalogo)

    if not cabecalho.get("data_laudo"):
        raise SystemExit("Não consegui identificar a data do laudo no PDF.")

    data_exame = data_br_para_iso(cabecalho["data_laudo"])
    if args.dry_run:
        paciente_id = encontrar_paciente_sem_criar(cabecalho, args.paciente_id) or "NOVO_PACIENTE"
    else:
        paciente_id = encontrar_ou_criar_paciente(cabecalho, args.paciente_id)

    print("Paciente PDF:", cabecalho.get("nome"))
    print("Paciente ID:", paciente_id)
    print("Data exame:", data_exame)
    print("Ficha:", cabecalho.get("ficha"))
    print("Parser: Fleury/F. Mattoso")
    print("Resultados encontrados:", len(resultados))

    for r in resultados:
        print(f'- {r["nome_exame"]}: {r["resultado"]} {r["unidade"]} | {r["status"]}')

    if args.dry_run:
        print("\nDry-run: nenhum CSV foi alterado.")
        return

    atualizar_catalogo(catalogo)
    importar_resultados(paciente_id, data_exame, resultados, cabecalho.get("ficha", ""))

    print("\nImportação concluída.")
    print("Arquivos atualizados:")
    print(DATA_FLET / "exames.csv")
    print(DATA_FLET / "analise_exames.csv")
    print(DATA_FLET / "referencias_exames.csv")
    print(DATA_FLET / "alias_exames.csv")


if __name__ == "__main__":
    main()

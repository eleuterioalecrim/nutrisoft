#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Patch NutriSoft:
Inclui a coluna "Referência aplicada" na tabela compacta "Exames alterados",
logo depois da coluna "Resultado".

Uso:
    cd ~/projetos/nutrisoft_pr_limpo
    python3 patch_coluna_referencia_exames_alterados.py
    python3 nutrisoft_flet_app.py
'''

from pathlib import Path
import py_compile
import shutil
from datetime import datetime


APP = Path("nutrisoft_flet_app.py")

if not APP.exists():
    raise SystemExit(
        "Arquivo nutrisoft_flet_app.py não encontrado. "
        "Execute este patch dentro da pasta do projeto NutriSoft."
    )

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup = backup_dir / f"nutrisoft_flet_app_antes_coluna_ref_exames_alterados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(APP, backup)

s = APP.read_text(encoding="utf-8")

# Remove tentativas anteriores deste ajuste.
BLOCOS_PARA_REMOVER = [
    (
        "# ===== PATCH ANALISE NUTRICIONAL: COLUNA REFERENCIA =====",
        "# ===== FIM PATCH ANALISE NUTRICIONAL: COLUNA REFERENCIA =====",
    ),
    (
        "# ===== PATCH EXAMES ALTERADOS: COLUNA REFERENCIA =====",
        "# ===== FIM PATCH EXAMES ALTERADOS: COLUNA REFERENCIA =====",
    ),
    (
        "# ===== PATCH DATATABLE EXAMES ALTERADOS: REFERENCIA APOS RESULTADO =====",
        "# ===== FIM PATCH DATATABLE EXAMES ALTERADOS: REFERENCIA APOS RESULTADO =====",
    ),
]

for inicio, fim in BLOCOS_PARA_REMOVER:
    while inicio in s and fim in s:
        ini = s.index(inicio)
        end = s.index(fim) + len(fim)
        s = s[:ini] + s[end:]


PATCH = r'''
# ===== PATCH DATATABLE EXAMES ALTERADOS: REFERENCIA APOS RESULTADO =====

import csv as _dtref_csv
import re as _dtref_re
import unicodedata as _dtref_unicodedata
from pathlib import Path as _dtref_Path


def _dtref_data_dir():
    try:
        return _patch_data_dir()
    except Exception:
        return _dtref_Path(__file__).resolve().parent / "data_flet"


def _dtref_norm(valor):
    texto = str(valor or "").strip().lower()
    texto = _dtref_unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not _dtref_unicodedata.combining(c))
    texto = texto.replace("_", " ").replace("-", " ")
    texto = _dtref_re.sub(r"[^a-z0-9%/., ]+", " ", texto)
    return " ".join(texto.split())


def _dtref_data_iso(valor):
    texto = str(valor or "").strip()

    m = _dtref_re.match(r"^(\d{2})/(\d{2})/(\d{4})$", texto)
    if m:
        dia, mes, ano = m.groups()
        return f"{ano}-{mes}-{dia}"

    return texto


def _dtref_texto_controle(ctrl):
    if ctrl is None:
        return ""

    for attr in ["value", "text"]:
        try:
            valor = getattr(ctrl, attr)
            if valor is not None and str(valor).strip():
                return str(valor).strip()
        except Exception:
            pass

    try:
        content = getattr(ctrl, "content", None)
        if content is not None:
            valor = _dtref_texto_controle(content)
            if valor:
                return valor
    except Exception:
        pass

    try:
        label = getattr(ctrl, "label", None)
        if label is not None:
            valor = _dtref_texto_controle(label)
            if valor:
                return valor
    except Exception:
        pass

    try:
        controls = getattr(ctrl, "controls", None)
        if controls:
            partes = []
            for c in controls:
                valor = _dtref_texto_controle(c)
                if valor:
                    partes.append(valor)
            return " ".join(partes).strip()
    except Exception:
        pass

    return ""


def _dtref_texto_coluna(col):
    try:
        return _dtref_texto_controle(col.label)
    except Exception:
        pass

    try:
        return _dtref_texto_controle(col.content)
    except Exception:
        pass

    return _dtref_texto_controle(col)


def _dtref_texto_celula(cell):
    try:
        return _dtref_texto_controle(cell.content)
    except Exception:
        return _dtref_texto_controle(cell)


def _dtref_ler_analises():
    caminho = _dtref_data_dir() / "analise_exames.csv"

    if not caminho.exists():
        return []

    with open(caminho, newline="", encoding="utf-8-sig") as f:
        reader = _dtref_csv.DictReader(f)
        return [
            {
                str(k or "").replace("\ufeff", "").strip(): "" if v is None else str(v).strip()
                for k, v in r.items()
            }
            for r in reader
        ]


def _dtref_referencia_por_linha(data_tabela, exame_tabela, resultado_tabela):
    data_iso = _dtref_data_iso(data_tabela)
    exame_n = _dtref_norm(exame_tabela)
    resultado_n = _dtref_norm(resultado_tabela)

    paciente_id = str(globals().get("PACIENTE_SELECIONADO_ID", "") or "").strip()
    if paciente_id.isdigit() and len(paciente_id) < 4:
        paciente_id = paciente_id.zfill(4)

    candidatos = []

    for r in _dtref_ler_analises():
        pid = str(r.get("paciente_id") or r.get("id_paciente") or "").strip()
        if pid.isdigit() and len(pid) < 4:
            pid = pid.zfill(4)

        if paciente_id and pid and pid != paciente_id:
            continue

        data = r.get("data_exame") or r.get("data") or ""

        nome = (
            r.get("nome_exame")
            or r.get("nome_padronizado")
            or r.get("exame_nome")
            or r.get("nome")
            or r.get("exame")
            or ""
        )

        resultado = f"{r.get('resultado', '')} {r.get('unidade', '')}".strip()

        data_match = not data_iso or not data or _dtref_data_iso(data) == data_iso

        exame_match = (
            exame_n
            and _dtref_norm(nome)
            and (
                exame_n == _dtref_norm(nome)
                or exame_n in _dtref_norm(nome)
                or _dtref_norm(nome) in exame_n
            )
        )

        resultado_match = True
        if resultado_n:
            resultado_match = (
                resultado_n == _dtref_norm(resultado)
                or resultado_n in _dtref_norm(resultado)
                or _dtref_norm(r.get("resultado")) in resultado_n
            )

        if data_match and exame_match and resultado_match:
            candidatos.append(r)

    if not candidatos:
        return "-"

    r = candidatos[0]
    ref = r.get("referencia") or r.get("referencia_texto") or ""

    if not ref:
        vmin = r.get("valor_min") or ""
        vmax = r.get("valor_max") or ""
        unidade = r.get("unidade") or ""

        if vmin and vmax:
            ref = f"{vmin} a {vmax} {unidade}".strip()
        elif vmin:
            ref = f">= {vmin} {unidade}".strip()
        elif vmax:
            ref = f"<= {vmax} {unidade}".strip()

    sexo = r.get("sexo_referencia") or ""
    idade_min = r.get("idade_min") or ""
    idade_max = r.get("idade_max") or ""

    if ref and (sexo or idade_min or idade_max):
        return f"{ref}\n{sexo or 'Todos'}, {idade_min or '0'}-{idade_max or '120'} anos"

    return ref or "-"


def _dtref_cell(texto, largura=170, negrito=False):
    return ft.Container(
        width=largura,
        padding=6,
        content=ft.Text(
            str(texto or "-"),
            size=10 if negrito else 11,
            weight=ft.FontWeight.BOLD if negrito else ft.FontWeight.NORMAL,
            color="#111827" if negrito else "#374151",
            no_wrap=False,
            max_lines=None,
            overflow=ft.TextOverflow.VISIBLE,
        ),
    )


def _dtref_scroll():
    try:
        return ft.ScrollMode.AUTO
    except Exception:
        return "auto"


def _dtref_linha_parece_exames_alterados(rows):
    if not rows:
        return False

    try:
        cells = list(rows[0].cells)
    except Exception:
        return False

    if len(cells) != 4:
        return False

    data_txt = _dtref_texto_celula(cells[0])
    status_txt = _dtref_norm(_dtref_texto_celula(cells[3]))

    data_ok = bool(
        _dtref_re.match(r"^\d{2}/\d{2}/\d{4}$", data_txt)
        or _dtref_re.match(r"^\d{4}-\d{2}-\d{2}$", data_txt)
    )

    status_ok = any(
        termo in status_txt
        for termo in ["alto", "baixo", "alterado", "critico", "sem analise", "normal"]
    )

    return data_ok and status_ok


try:
    _dtref_datatable_original
except NameError:
    _dtref_datatable_original = ft.DataTable


def _dtref_datatable_wrapper(*args, **kwargs):
    columns = kwargs.get("columns")
    rows = kwargs.get("rows")

    if columns is None and len(args) >= 1:
        try:
            if isinstance(args[0], list):
                columns = args[0]
        except Exception:
            pass

    if rows is None:
        rows = []

    labels = [_dtref_norm(_dtref_texto_coluna(c)) for c in (columns or [])]

    alvo_por_labels = (
        len(labels) == 4
        and labels[0] == "data"
        and labels[1] == "exame"
        and labels[2] == "resultado"
        and labels[3] == "status"
    )

    alvo_por_linha = (
        len(columns or []) == 4
        and _dtref_linha_parece_exames_alterados(rows)
    )

    if not (alvo_por_labels or alvo_por_linha):
        return _dtref_datatable_original(*args, **kwargs)

    novas_colunas = [
        columns[0],
        columns[1],
        columns[2],
        ft.DataColumn(_dtref_cell("Referência aplicada", 230, negrito=True)),
        columns[3],
    ]

    novas_linhas = []

    for row in rows or []:
        try:
            cells = list(row.cells)
        except Exception:
            novas_linhas.append(row)
            continue

        if len(cells) != 4:
            novas_linhas.append(row)
            continue

        data_txt = _dtref_texto_celula(cells[0])
        exame_txt = _dtref_texto_celula(cells[1])
        resultado_txt = _dtref_texto_celula(cells[2])

        ref_txt = _dtref_referencia_por_linha(
            data_txt,
            exame_txt,
            resultado_txt,
        )

        novas_cells = [
            cells[0],
            cells[1],
            cells[2],
            ft.DataCell(_dtref_cell(ref_txt, 230)),
            cells[3],
        ]

        try:
            novas_linhas.append(ft.DataRow(cells=novas_cells))
        except Exception:
            novas_linhas.append(row)

    base_dt = globals().get("_patch_ft_datatable_original", _dtref_datatable_original)

    tabela = base_dt(
        columns=novas_colunas,
        rows=novas_linhas,
        column_spacing=8,
        horizontal_margin=8,
    )

    return ft.Row(
        scroll=_dtref_scroll(),
        controls=[tabela],
    )


ft.DataTable = _dtref_datatable_wrapper

# ===== FIM PATCH DATATABLE EXAMES ALTERADOS: REFERENCIA APOS RESULTADO =====
'''

marker = '\nif __name__ == "__main__":'
idx = s.rfind(marker)

if idx == -1:
    APP.write_text(s, encoding="utf-8")
    raise SystemExit('Não encontrei if __name__ == "__main__". Patch não aplicado.')

s = s[:idx] + "\n\n" + PATCH + "\n\n" + s[idx:]

APP.write_text(s, encoding="utf-8")

try:
    py_compile.compile(str(APP), doraise=True)
except Exception:
    shutil.copy2(backup, APP)
    raise SystemExit(
        "O patch gerou erro de compilação. "
        f"O backup foi restaurado automaticamente: {backup}"
    )

print("Patch aplicado com sucesso.")
print(f"Backup criado em: {backup}")
print("Agora rode: python3 nutrisoft_flet_app.py")

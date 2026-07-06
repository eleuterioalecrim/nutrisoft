#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Patch NutriSoft:
Corrige definitivamente a lista "Já cadastrados na data" e a lista de exames disponíveis.

Problema corrigido:
- O exame era gravado nos CSVs, mas não aparecia em "Já cadastrados na data".
- O exame recém-gravado continuava aparecendo como disponível para lançamento.
- Isso ocorria por diferença entre nome/id/tokens do catálogo e o que foi gravado em analise_exames.csv.

Estratégia:
- A lista "Já cadastrados na data" passa a ser montada diretamente de analise_exames.csv,
  filtrando por paciente_id + data_exame.
- A lista de disponíveis passa a remover qualquer exame cujo token bata com os já gravados.
- O cache é limpo logo após salvar e excluir.

Uso:
    cd ~/projetos/nutrisoft_pr_limpo
    python3 patch_lista_cadastrados_definitiva.py
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

backup = backup_dir / f"nutrisoft_flet_app_antes_lista_cadastrados_definitiva_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(APP, backup)

s = APP.read_text(encoding="utf-8")

inicio = "# ===== PATCH LISTA CADASTRADOS DEFINITIVA CSV ====="
fim = "# ===== FIM PATCH LISTA CADASTRADOS DEFINITIVA CSV ====="

while inicio in s and fim in s:
    ini = s.index(inicio)
    end = s.index(fim) + len(fim)
    s = s[:ini] + s[end:]


PATCH = r'''
# ===== PATCH LISTA CADASTRADOS DEFINITIVA CSV =====

import csv as _lcd_csv
import re as _lcd_re
import unicodedata as _lcd_unicodedata
from pathlib import Path as _lcd_Path


def _lcd_data_dir():
    try:
        return _patch_data_dir()
    except Exception:
        return _lcd_Path(__file__).resolve().parent / "data_flet"


def _lcd_norm(valor):
    texto = str(valor or "").strip().lower()
    texto = _lcd_unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not _lcd_unicodedata.combining(c))
    texto = texto.replace("_", " ").replace("-", " ")
    texto = _lcd_re.sub(r"[^a-z0-9%/., ]+", " ", texto)
    return " ".join(texto.split())


def _lcd_id(valor):
    texto = _lcd_norm(valor)
    texto = _lcd_re.sub(r"[^a-z0-9]+", "_", texto).strip("_")
    return texto


def _lcd_get(row, *campos):
    if not isinstance(row, dict):
        return ""

    limpo = {
        str(k or "").replace("\ufeff", "").strip(): "" if v is None else str(v).strip()
        for k, v in row.items()
    }

    for campo in campos:
        valor = limpo.get(str(campo or "").strip(), "")
        if valor:
            return valor

    return ""


def _lcd_data_iso(valor):
    texto = str(valor or "").strip()

    m = _lcd_re.match(r"^(\d{2})/(\d{2})/(\d{4})$", texto)
    if m:
        dia, mes, ano = m.groups()
        return f"{ano}-{mes}-{dia}"

    m = _lcd_re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", texto)
    if m:
        ano, mes, dia = m.groups()
        return f"{ano}-{int(mes):02d}-{int(dia):02d}"

    return texto


def _lcd_pid(valor):
    pid = str(valor or "").strip()
    if pid.isdigit() and len(pid) < 4:
        pid = pid.zfill(4)
    return pid


def _lcd_ler_csv(nome):
    caminho = _lcd_data_dir() / nome

    if not caminho.exists():
        return []

    with open(caminho, newline="", encoding="utf-8-sig") as f:
        reader = _lcd_csv.DictReader(f)
        return [
            {
                str(k or "").replace("\ufeff", "").strip(): "" if v is None else str(v).strip()
                for k, v in r.items()
            }
            for r in reader
        ]


def _lcd_nome_exame(row):
    nome = _lcd_get(
        row,
        "nome_exame",
        "nome_padronizado",
        "exame_nome",
        "nome",
        "exame",
        "descricao",
        "analito",
        "id",
    )

    if nome and nome not in ["-", "None", "null"]:
        return nome

    return ""


def _lcd_tokens_nome(nome):
    tokens = set()

    nome = str(nome or "").strip()
    if not nome:
        return tokens

    tokens.add(_lcd_norm(nome))
    tokens.add(_lcd_id(nome))

    aliases = {
        "ferritina": ["ferritina", "ferr"],
        "ferro": ["ferro", "ferro_serico"],
        "saturacao_da_transferrina": [
            "saturacao_da_transferrina",
            "saturacao_transferrina",
            "transferrina_saturacao",
        ],
        "glicose": ["glicose", "glicemia", "glucose"],
        "hemoglobina_glicada": ["hemoglobina_glicada", "hba1c", "glicada"],
        "colesterol_total": ["colesterol_total", "colesterol"],
        "triglicerideos": ["triglicerideos", "triglicerides", "trig"],
        "creatinina": ["creatinina", "creat"],
    }

    base = _lcd_id(nome)

    for canon, vals in aliases.items():
        vals_norm = {_lcd_id(v) for v in vals}
        vals_norm.add(canon)

        if base in vals_norm:
            tokens.update(vals_norm)

    return {t for t in tokens if t}


def _lcd_tokens_item(item):
    tokens = set()

    if isinstance(item, dict):
        for campo in [
            "id",
            "id_canonico",
            "nome_exame",
            "nome_padronizado",
            "exame_nome",
            "nome",
            "exame",
            "descricao",
            "analito",
        ]:
            valor = _lcd_get(item, campo)
            tokens.update(_lcd_tokens_nome(valor))

        nome = _lcd_nome_exame(item)
        if nome:
            tokens.update(_lcd_tokens_nome(nome))
    else:
        tokens.update(_lcd_tokens_nome(item))

    return {t for t in tokens if t}


def _lcd_referencia_resumo(row):
    ref = _lcd_get(row, "referencia", "referencia_texto")

    if not ref:
        vmin = _lcd_get(row, "valor_min")
        vmax = _lcd_get(row, "valor_max")
        unidade = _lcd_get(row, "unidade")

        if vmin and vmax:
            ref = f"{vmin} - {vmax} {unidade}".strip()
        elif vmin:
            ref = f">= {vmin} {unidade}".strip()
        elif vmax:
            ref = f"<= {vmax} {unidade}".strip()

    return ref


def _lcd_item_cadastrado(row):
    nome = _lcd_nome_exame(row)
    grupo = _lcd_get(row, "grupo")

    if not grupo:
        try:
            ref = _patch_ref(nome)
            grupo = _patch_get(ref, "grupo")
        except Exception:
            grupo = ""

    if not grupo:
        try:
            grupo = _patch_grupo_exame_correto(nome, "")
        except Exception:
            grupo = ""

    referencia = _lcd_referencia_resumo(row)

    fonte = _lcd_get(row, "fonte_referencia", "fonte")
    if not fonte:
        try:
            ref = _patch_ref(nome)
            fonte = _patch_get(ref, "fonte_referencia", "fonte")
        except Exception:
            fonte = ""

    item = dict(row)
    item.update({
        "id": _lcd_id(nome),
        "id_canonico": _lcd_id(nome),
        "nome": nome,
        "nome_exame": nome,
        "exame_nome": nome,
        "exame": nome,
        "grupo": grupo,
        "referencia": referencia,
        "referencia_texto": referencia,
        "fonte": fonte,
        "fonte_referencia": fonte,
    })

    return item


def _lcd_linhas_cadastradas_csv(paciente_id, data_exame):
    pid_alvo = _lcd_pid(paciente_id)
    data_alvo = _lcd_data_iso(data_exame)

    linhas = []

    # analise_exames.csv é a fonte mais completa para exibir referência/status.
    for row in _lcd_ler_csv("analise_exames.csv"):
        pid = _lcd_pid(_lcd_get(row, "paciente_id", "id_paciente"))
        data = _lcd_data_iso(_lcd_get(row, "data_exame", "data"))

        if pid == pid_alvo and data == data_alvo:
            nome = _lcd_nome_exame(row)
            if nome:
                linhas.append(_lcd_item_cadastrado(row))

    # fallback: se o exame existe só em exames.csv por algum erro antigo.
    tokens_existentes = set()
    for item in linhas:
        tokens_existentes.update(_lcd_tokens_item(item))

    for row in _lcd_ler_csv("exames.csv"):
        pid = _lcd_pid(_lcd_get(row, "paciente_id", "id_paciente"))
        data = _lcd_data_iso(_lcd_get(row, "data_exame", "data"))

        if pid != pid_alvo or data != data_alvo:
            continue

        nome = _lcd_nome_exame(row)
        tokens = _lcd_tokens_nome(nome)

        if not nome or (tokens and tokens & tokens_existentes):
            continue

        linhas.append(_lcd_item_cadastrado(row))
        tokens_existentes.update(tokens)

    # Dedup final por token canônico.
    saida = []
    vistos = set()

    for item in linhas:
        tokens = _lcd_tokens_item(item)
        chave = sorted(tokens)[0] if tokens else _lcd_id(_lcd_nome_exame(item))

        if chave in vistos:
            continue

        vistos.add(chave)
        saida.append(item)

    saida.sort(key=lambda x: _lcd_norm(_lcd_nome_exame(x)))

    return saida


try:
    _lcd_exames_ja_original
except NameError:
    _lcd_exames_ja_original = exames_ja_cadastrados_por_data


def exames_ja_cadastrados_por_data(paciente_id, data_exame):
    linhas = _lcd_linhas_cadastradas_csv(paciente_id, data_exame)

    try:
        globals()["EXAMES_CADASTRADOS_MOCK"] = {
            (
                _lcd_pid(paciente_id),
                _lcd_data_iso(data_exame),
            ): [
                item.get("id") or item.get("id_canonico") or _lcd_id(_lcd_nome_exame(item))
                for item in linhas
            ]
        }
    except Exception:
        pass

    return linhas


try:
    _lcd_disponiveis_original
except NameError:
    _lcd_disponiveis_original = exames_disponiveis_por_data


def exames_disponiveis_por_data(paciente_id, data_exame):
    try:
        lista = _lcd_disponiveis_original(paciente_id, data_exame)
    except Exception:
        lista = []

    cadastrados = _lcd_linhas_cadastradas_csv(paciente_id, data_exame)

    tokens_bloqueados = set()
    for item in cadastrados:
        tokens_bloqueados.update(_lcd_tokens_item(item))

    disponiveis = []

    for exame in lista or []:
        tokens_exame = _lcd_tokens_item(exame)

        if tokens_exame and tokens_exame & tokens_bloqueados:
            continue

        disponiveis.append(exame)

    return disponiveis


def _lcd_refresh_pos_operacao_exame():
    try:
        if "_perf_limpar_cache" in globals():
            _perf_limpar_cache()
    except Exception:
        pass

    try:
        sincronizar_resultados_exames_mock_data_flet()
    except Exception as exc:
        print(f"[LISTA CADASTRADOS] Falha ao sincronizar resultados: {exc}")

    try:
        atualizar_pacientes_csv_real_definitivo()
    except Exception as exc:
        print(f"[LISTA CADASTRADOS] Falha ao atualizar pacientes: {exc}")


try:
    _lcd_salvar_definitivo_original
except NameError:
    _lcd_salvar_definitivo_original = salvar_resultado_exame_csv_definitivo


def salvar_resultado_exame_csv_definitivo(item):
    ok = _lcd_salvar_definitivo_original(item)

    if ok:
        _lcd_refresh_pos_operacao_exame()
        print("[LISTA CADASTRADOS] Índice atualizado após salvar exame.")

    return ok


try:
    _lcd_excluir_original
except NameError:
    _lcd_excluir_original = excluir_exame_cadastrado_errado


def excluir_exame_cadastrado_errado(paciente_id, data_exame, exame):
    total = _lcd_excluir_original(paciente_id, data_exame, exame)

    if total:
        _lcd_refresh_pos_operacao_exame()
        print("[LISTA CADASTRADOS] Índice atualizado após excluir exame.")

    return total

# ===== FIM PATCH LISTA CADASTRADOS DEFINITIVA CSV =====
'''

marker = '\nif __name__ == "__main__":'
idx = s.rfind(marker)

if idx == -1:
    shutil.copy2(backup, APP)
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

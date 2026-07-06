#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Patch NutriSoft:
Corrige definitivamente o salvamento de exames cadastrados pela tela "Exames".

Problema corrigido:
- A tela mostrava snackbar de sucesso mesmo quando o exame não era gravado no CSV.
- O salvamento dependia de RESULTADOS_EXAMES_MOCK.append(), que podia virar lista comum após sync/cache.
- Agora o botão Salvar grava diretamente em:
    data_flet/exames.csv
    data_flet/analise_exames.csv
  e só depois exibe mensagem de sucesso.

Uso:
    cd ~/projetos/nutrisoft_pr_limpo
    python3 patch_salvamento_definitivo_exames.py
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

backup = backup_dir / f"nutrisoft_flet_app_antes_salvamento_definitivo_exames_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(APP, backup)

s = APP.read_text(encoding="utf-8")

# Remove patch anterior, se existir.
inicio = "# ===== PATCH SALVAMENTO DEFINITIVO EXAMES CSV ====="
fim = "# ===== FIM PATCH SALVAMENTO DEFINITIVO EXAMES CSV ====="

while inicio in s and fim in s:
    ini = s.index(inicio)
    end = s.index(fim) + len(fim)
    s = s[:ini] + s[end:]


PATCH = r'''
# ===== PATCH SALVAMENTO DEFINITIVO EXAMES CSV =====

import csv as _sdef_csv
import re as _sdef_re
import unicodedata as _sdef_unicodedata
from pathlib import Path as _sdef_Path


def _sdef_data_dir():
    try:
        return _patch_data_dir()
    except Exception:
        return _sdef_Path(__file__).resolve().parent / "data_flet"


def _sdef_norm(valor):
    texto = str(valor or "").strip().lower()
    texto = _sdef_unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not _sdef_unicodedata.combining(c))
    texto = texto.replace("_", " ").replace("-", " ")
    texto = _sdef_re.sub(r"[^a-z0-9%/., ]+", " ", texto)
    return " ".join(texto.split())


def _sdef_get(row, *campos):
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


def _sdef_ler_csv(nome):
    caminho = _sdef_data_dir() / nome

    if not caminho.exists():
        return [], []

    with open(caminho, newline="", encoding="utf-8-sig") as f:
        reader = _sdef_csv.DictReader(f)
        campos = [
            str(c or "").replace("\ufeff", "").strip()
            for c in (reader.fieldnames or [])
        ]
        rows = []
        for r in reader:
            rows.append({
                str(k or "").replace("\ufeff", "").strip(): "" if v is None else str(v).strip()
                for k, v in r.items()
            })

    return campos, rows


def _sdef_salvar_csv(nome, campos, rows):
    caminho = _sdef_data_dir() / nome
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")

    campos = list(campos or [])

    for r in rows:
        for k in r.keys():
            if k not in campos:
                campos.append(k)

    with open(tmp, "w", newline="", encoding="utf-8-sig") as f:
        writer = _sdef_csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({c: r.get(c, "") for c in campos})

    tmp.replace(caminho)


def _sdef_data_iso(valor):
    texto = str(valor or "").strip()

    m = _sdef_re.match(r"^(\d{2})/(\d{2})/(\d{4})$", texto)
    if m:
        dia, mes, ano = m.groups()
        return f"{ano}-{mes}-{dia}"

    return texto


def _sdef_pid(item):
    pid = _sdef_get(item, "paciente_id", "id_paciente")

    if not pid:
        try:
            pid = _patch_pid(item)
        except Exception:
            pid = ""

    pid = str(pid or "").strip()

    if pid.isdigit() and len(pid) < 4:
        pid = pid.zfill(4)

    return pid


def _sdef_nome_exame(item):
    nome = _sdef_get(
        item,
        "nome_exame",
        "exame_nome",
        "nome_padronizado",
        "nome",
        "exame",
        "analito",
        "descricao",
    )

    if nome and nome not in ["-", "None", "null"]:
        return nome

    try:
        nome = _patch_nome_exame(item)
        if nome and nome not in ["-", "None", "null"]:
            return nome
    except Exception:
        pass

    return ""


def _sdef_resultado(item):
    return _sdef_get(item, "resultado", "valor", "valor_resultado", "resultado_exame")


def _sdef_unidade(item):
    return _sdef_get(item, "unidade")


def _sdef_chave(row):
    pid = _sdef_pid(row)
    data = _sdef_data_iso(_sdef_get(row, "data_exame", "data"))
    nome = _sdef_nome_exame(row)
    resultado = _sdef_resultado(row)
    unidade = _sdef_unidade(row)

    return (
        pid,
        _sdef_norm(data),
        _sdef_norm(nome),
        _sdef_norm(resultado),
        _sdef_norm(unidade),
    )


def _sdef_proximo_id(rows, campo, largura=0):
    maior = 0

    for r in rows:
        valor = _sdef_get(r, campo)
        m = _sdef_re.search(r"\d+", str(valor or ""))
        if m:
            try:
                maior = max(maior, int(m.group(0)))
            except Exception:
                pass

    novo = maior + 1
    return str(novo).zfill(largura) if largura else str(novo)


def _sdef_analise(item):
    pid = _sdef_pid(item)
    nome = _sdef_nome_exame(item)
    resultado = _sdef_resultado(item)
    unidade = _sdef_unidade(item)

    try:
        analise = analisar_resultado_sexo_idade(nome, resultado, unidade, pid)
        if isinstance(analise, dict):
            return analise
    except Exception as exc:
        print(f"[SALVAR EXAME DEFINITIVO] Falha análise sexo/idade, usando fallback: {exc}")

    try:
        analise = _patch_analisar(nome, resultado, unidade)
        if isinstance(analise, dict):
            return analise
    except Exception as exc:
        print(f"[SALVAR EXAME DEFINITIVO] Falha análise fallback: {exc}")

    return {
        "nome_padronizado": nome,
        "valor_min": "",
        "valor_max": "",
        "status": "Sem análise",
        "mensagem": f"{nome}: {resultado} {unidade}",
        "referencia": _sdef_get(item, "referencia", "referencia_texto"),
        "referencia_texto": _sdef_get(item, "referencia", "referencia_texto"),
        "fonte_referencia": _sdef_get(item, "fonte_referencia", "fonte"),
        "fonte_url": _sdef_get(item, "fonte_url"),
        "sexo_referencia": "",
        "idade_min": "",
        "idade_max": "",
    }


def _sdef_limpar_cache():
    try:
        if "_perf_limpar_cache" in globals():
            _perf_limpar_cache()
    except Exception as exc:
        print(f"[SALVAR EXAME DEFINITIVO] Falha ao limpar cache de performance: {exc}")

    globals()["EXAMES_CADASTRADOS_MOCK"] = {}

    for nome_cache in [
        "_PERF_CSV_CACHE",
        "_PERF_DISPONIVEIS_CACHE",
        "_PERF_BLOQUEADOS_CACHE",
    ]:
        try:
            cache = globals().get(nome_cache)
            if hasattr(cache, "clear"):
                cache.clear()
        except Exception:
            pass

    for nome_cache in [
        "_PERF_REFS_CACHE",
        "_PERF_PACIENTES_CACHE",
        "_PERF_CADASTRADOS_CACHE",
        "_PERF_SYNC_CACHE",
        "_PERF_PACIENTES_UI_CACHE",
    ]:
        try:
            cache = globals().get(nome_cache)
            if isinstance(cache, dict):
                cache["key"] = None
                cache["value"] = None
        except Exception:
            pass


def salvar_resultado_exame_csv_definitivo(item):
    if not isinstance(item, dict):
        print("[SALVAR EXAME DEFINITIVO] Item inválido:", item)
        return False

    pid = _sdef_pid(item)
    data_exame = _sdef_data_iso(_sdef_get(item, "data_exame", "data"))
    nome_exame = _sdef_nome_exame(item)
    resultado = _sdef_resultado(item)
    unidade = _sdef_unidade(item)

    if not pid or not data_exame or not nome_exame or not resultado:
        print(
            "[SALVAR EXAME DEFINITIVO] Dados mínimos ausentes:",
            {
                "paciente_id": pid,
                "data_exame": data_exame,
                "nome_exame": nome_exame,
                "resultado": resultado,
                "item": item,
            },
        )
        return False

    analise = _sdef_analise(item)

    if not unidade:
        unidade = _sdef_get(analise, "unidade")
        if not unidade:
            try:
                ref = buscar_referencia_sexo_idade(nome_exame, pid)
                unidade = _sdef_get(ref, "unidade")
            except Exception:
                unidade = ""

    item["paciente_id"] = pid
    item["data"] = data_exame
    item["data_exame"] = data_exame
    item["nome_exame"] = nome_exame
    item["exame_nome"] = nome_exame
    item["nome"] = nome_exame
    item["exame"] = nome_exame
    item["resultado"] = resultado
    item["unidade"] = unidade
    item["status"] = _sdef_get(analise, "status") or "Sem análise"
    item["referencia"] = _sdef_get(analise, "referencia", "referencia_texto")
    item["referencia_texto"] = item["referencia"]
    item["fonte_referencia"] = _sdef_get(analise, "fonte_referencia", "fonte")
    item["fonte_url"] = _sdef_get(analise, "fonte_url")
    item["sexo_referencia"] = _sdef_get(analise, "sexo_referencia")
    item["idade_min"] = _sdef_get(analise, "idade_min")
    item["idade_max"] = _sdef_get(analise, "idade_max")

    campos_exames, exames = _sdef_ler_csv("exames.csv")
    campos_analise, analises = _sdef_ler_csv("analise_exames.csv")

    chave = _sdef_chave(item)

    chaves_exames = {_sdef_chave(r) for r in exames}
    chaves_analises = {_sdef_chave(r) for r in analises}

    mudou = False

    if chave not in chaves_exames:
        exames.append({
            "exame_id": _sdef_proximo_id(exames, "exame_id", 4),
            "paciente_id": pid,
            "data_exame": data_exame,
            "nome_exame": nome_exame,
            "resultado": resultado,
            "unidade": unidade,
            "observacoes": _sdef_get(item, "observacoes", "observacao", "obs") or "Lançado pela interface NutriSoft",
        })

        for c in ["exame_id", "paciente_id", "data_exame", "nome_exame", "resultado", "unidade", "observacoes"]:
            if c not in campos_exames:
                campos_exames.append(c)

        _sdef_salvar_csv("exames.csv", campos_exames, exames)
        mudou = True

    if chave not in chaves_analises:
        analises.append({
            "analise_id": _sdef_proximo_id(analises, "analise_id"),
            "paciente_id": pid,
            "data_exame": data_exame,
            "nome_exame": nome_exame,
            "nome_padronizado": _sdef_get(analise, "nome_padronizado") or nome_exame,
            "resultado": resultado,
            "unidade": unidade,
            "valor_min": _sdef_get(analise, "valor_min"),
            "valor_max": _sdef_get(analise, "valor_max"),
            "status": _sdef_get(analise, "status") or "Sem análise",
            "mensagem": _sdef_get(analise, "mensagem"),
            "referencia": _sdef_get(analise, "referencia", "referencia_texto"),
            "referencia_texto": _sdef_get(analise, "referencia", "referencia_texto"),
            "fonte_referencia": _sdef_get(analise, "fonte_referencia", "fonte"),
            "fonte_url": _sdef_get(analise, "fonte_url"),
            "sexo_referencia": _sdef_get(analise, "sexo_referencia"),
            "idade_min": _sdef_get(analise, "idade_min"),
            "idade_max": _sdef_get(analise, "idade_max"),
        })

        for c in [
            "analise_id",
            "paciente_id",
            "data_exame",
            "nome_exame",
            "nome_padronizado",
            "resultado",
            "unidade",
            "valor_min",
            "valor_max",
            "status",
            "mensagem",
            "referencia",
            "referencia_texto",
            "fonte_referencia",
            "fonte_url",
            "sexo_referencia",
            "idade_min",
            "idade_max",
        ]:
            if c not in campos_analise:
                campos_analise.append(c)

        _sdef_salvar_csv("analise_exames.csv", campos_analise, analises)
        mudou = True

    _sdef_limpar_cache()

    if mudou:
        print(
            f"[SALVAR EXAME DEFINITIVO] Gravado em CSV: paciente={pid} | "
            f"data={data_exame} | exame={nome_exame} | resultado={resultado} {unidade} | "
            f"status={item['status']}"
        )
    else:
        print(
            f"[SALVAR EXAME DEFINITIVO] Registro já existia no CSV: paciente={pid} | "
            f"data={data_exame} | exame={nome_exame} | resultado={resultado} {unidade}"
        )

    return True

# ===== FIM PATCH SALVAMENTO DEFINITIVO EXAMES CSV =====
'''

marker = '\nif __name__ == "__main__":'
idx = s.rfind(marker)

if idx == -1:
    shutil.copy2(backup, APP)
    raise SystemExit('Não encontrei if __name__ == "__main__". Patch não aplicado.')

s = s[:idx] + "\n\n" + PATCH + "\n\n" + s[idx:]


# Substitui o miolo do salvar() dentro de exame_disponivel_card().
try:
    func_ini = s.index("def exame_disponivel_card(")
    salvar_ini = s.index("        def salvar(ev):", func_ini)
    inicio_bloco = s.index("            if chave not in EXAMES_CADASTRADOS_MOCK:", salvar_ini)
    fim_bloco = s.index("            if atualizar_callback:", inicio_bloco)
except ValueError as exc:
    shutil.copy2(backup, APP)
    raise SystemExit(
        "Não encontrei o bloco de salvamento antigo dentro de exame_disponivel_card(). "
        f"Backup restaurado: {backup}. Erro: {exc}"
    )

NOVO_BLOCO = r'''            item_resultado = {
                "paciente_id": paciente_id,
                "paciente_nome": nome_paciente_por_id(paciente_id),
                "data": data_exame,
                "data_exame": data_exame,
                "exame_id": exame["id"],
                "nome_exame": exame["nome"],
                "nome": exame["nome"],
                "exame": exame["nome"],
                "exame_nome": exame["nome"],
                "grupo": detalhe_ref_popup["grupo"],
                "resultado": valor,
                "unidade": unidade.value,
                "referencia": detalhe_ref_popup["referencia"],
                "referencia_texto": detalhe_ref_popup["referencia"],
                "fonte": detalhe_ref_popup["fonte"],
                "fonte_referencia": detalhe_ref_popup["fonte"],
                "observacao": observacao.value or "",
                "observacoes": observacao.value or "",
            }

            persistiu = salvar_resultado_exame_csv_definitivo(item_resultado)

            if not persistiu:
                mostrar_snackbar(
                    page,
                    f'Não foi possível salvar o exame "{exame["nome"]}" nos arquivos CSV.',
                    COR_CRITICO,
                )
                return

            status_resultado = item_resultado.get("status") or analisar_resultado_por_referencia(
                valor,
                detalhe_ref_popup["referencia"],
            )

            if chave not in EXAMES_CADASTRADOS_MOCK:
                EXAMES_CADASTRADOS_MOCK[chave] = []

            if exame["id"] not in EXAMES_CADASTRADOS_MOCK[chave]:
                EXAMES_CADASTRADOS_MOCK[chave].append(exame["id"])

            # Mantém a memória visual atualizada, mas não depende mais do append para gravar no CSV.
            try:
                ja_memoria = False
                for r in list(RESULTADOS_EXAMES_MOCK):
                    mesmo_paciente = str(r.get("paciente_id", "")).zfill(4) == str(paciente_id).zfill(4)
                    mesmo_exame = str(r.get("nome_exame") or r.get("exame_nome") or r.get("nome") or "") == exame["nome"]
                    mesmo_data = str(r.get("data_exame") or r.get("data") or "") == data_exame
                    mesmo_resultado = str(r.get("resultado") or "") == str(valor)
                    if mesmo_paciente and mesmo_exame and mesmo_data and mesmo_resultado:
                        ja_memoria = True
                        break

                if not ja_memoria:
                    list.append(RESULTADOS_EXAMES_MOCK, item_resultado)
            except Exception as exc:
                print(f"[SALVAR EXAME DEFINITIVO] Exame salvo, mas falhou atualização da memória: {exc}")

            try:
                sincronizar_resultados_exames_mock_data_flet()
                atualizar_pacientes_csv_real_definitivo()
            except Exception as exc:
                print(f"[SALVAR EXAME DEFINITIVO] Exame salvo, mas falhou atualização pós-salvamento: {exc}")

            dialog.open = False
            mostrar_snackbar(
                page,
                f'"{exame["nome"]}" salvo como {status_resultado}.',
                cor_resultado_exame(status_resultado),
            )

'''

s = s[:inicio_bloco] + NOVO_BLOCO + s[fim_bloco:]

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

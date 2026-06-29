import csv
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from src.config import BASE_DIR, DATA_DIR, REPORTS_DIR, CSV_FILES
from src.database import ler_csv, salvar_csv
from src.pacientes import buscar_paciente_por_id


BASES_COM_PACIENTE = [
    "pacientes",
    "anamnese",
    "recordatorio_habitual",
    "antropometria",
    "exames",
    "analise_exames",
    "evolucao_conduta",
]

# histórico_edicoes não possui paciente_id em todas as versões.
# Ele será preservado por padrão para rastreabilidade do sistema.
BASES_PRESERVADAS = [
    "historico_edicoes",
    "referencias_exames",
    "alias_exames",
]


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _safe(texto: str) -> str:
    texto = str(texto or "").strip()
    permitido = []
    for c in texto:
        if c.isalnum() or c in ["-", "_"]:
            permitido.append(c)
        elif c.isspace():
            permitido.append("_")
    saida = "".join(permitido).strip("_")
    return saida[:80] or "paciente"


def _linha_do_paciente(base: str, linha: dict, paciente_id: str) -> bool:
    if base == "pacientes":
        return str(linha.get("paciente_id", "")).strip() == str(paciente_id).strip()

    return str(linha.get("paciente_id", "")).strip() == str(paciente_id).strip()


def contar_dados_paciente(paciente_id: str) -> dict:
    paciente = buscar_paciente_por_id(paciente_id)
    contagens = {}

    for base in BASES_COM_PACIENTE:
        linhas = ler_csv(base)
        contagens[base] = sum(1 for linha in linhas if _linha_do_paciente(base, linha, paciente_id))

    arquivos = listar_arquivos_gerados_paciente(paciente_id)

    return {
        "paciente": paciente,
        "contagens": contagens,
        "total_registros": sum(contagens.values()),
        "arquivos_gerados": arquivos,
        "total_arquivos": len(arquivos),
    }


def listar_arquivos_gerados_paciente(paciente_id: str) -> list[str]:
    arquivos = []

    if not REPORTS_DIR.exists():
        return arquivos

    paciente_id = str(paciente_id).strip()

    for arquivo in REPORTS_DIR.rglob("*"):
        if not arquivo.is_file():
            continue

        nome = arquivo.name.lower()
        caminho = str(arquivo)

        # A maioria dos relatórios gerados contém o ID no nome.
        if paciente_id.lower() in nome:
            arquivos.append(caminho)

    return sorted(arquivos)


def _salvar_csv_backup(caminho: Path, linhas: list[dict]):
    if not linhas:
        return

    caminho.parent.mkdir(parents=True, exist_ok=True)

    campos = sorted({campo for linha in linhas for campo in linha.keys()})
    with caminho.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(linhas)


def criar_backup_paciente(paciente_id: str) -> dict:
    info = contar_dados_paciente(paciente_id)
    paciente = info.get("paciente") or {}

    nome = _safe(paciente.get("nome", "paciente"))
    ts = _timestamp()

    backup_dir = BASE_DIR / "backups" / "pacientes_excluidos" / f"{paciente_id}_{nome}_{ts}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "paciente_id": paciente_id,
        "paciente": paciente,
        "data_backup": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "bases": {},
        "arquivos_gerados": [],
    }

    for base in BASES_COM_PACIENTE:
        linhas = ler_csv(base)
        linhas_paciente = [linha for linha in linhas if _linha_do_paciente(base, linha, paciente_id)]
        manifest["bases"][base] = len(linhas_paciente)
        _salvar_csv_backup(backup_dir / f"{base}.csv", linhas_paciente)

    arquivos = listar_arquivos_gerados_paciente(paciente_id)
    arquivos_dir = backup_dir / "arquivos_gerados"
    arquivos_dir.mkdir(parents=True, exist_ok=True)

    for arquivo in arquivos:
        origem = Path(arquivo)
        if origem.exists() and origem.is_file():
            destino = arquivos_dir / origem.name
            shutil.copy2(origem, destino)
            manifest["arquivos_gerados"].append(str(destino))

    (backup_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    zip_path = backup_dir.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for arquivo in backup_dir.rglob("*"):
            if arquivo.is_file():
                zipf.write(arquivo, arquivo.relative_to(backup_dir.parent))

    return {
        "backup_dir": str(backup_dir),
        "backup_zip": str(zip_path),
        "manifest": manifest,
    }


def excluir_dados_paciente(
    paciente_id: str,
    confirmar_texto: str,
    excluir_arquivos_gerados: bool = True,
    criar_backup: bool = True,
) -> dict:
    paciente = buscar_paciente_por_id(paciente_id)

    if not paciente:
        return {
            "sucesso": False,
            "erro": "Paciente não encontrado.",
            "backup": None,
            "removidos": {},
            "arquivos_removidos": [],
        }

    texto_esperado = f"EXCLUIR {paciente_id}"
    if str(confirmar_texto).strip() != texto_esperado:
        return {
            "sucesso": False,
            "erro": f"Confirmação inválida. Digite exatamente: {texto_esperado}",
            "backup": None,
            "removidos": {},
            "arquivos_removidos": [],
        }

    backup = criar_backup_paciente(paciente_id) if criar_backup else None

    removidos = {}

    for base in BASES_COM_PACIENTE:
        linhas = ler_csv(base)
        manter = [linha for linha in linhas if not _linha_do_paciente(base, linha, paciente_id)]
        removidos[base] = len(linhas) - len(manter)
        salvar_csv(base, manter)

    arquivos_removidos = []
    if excluir_arquivos_gerados:
        for arquivo in listar_arquivos_gerados_paciente(paciente_id):
            path = Path(arquivo)
            if path.exists() and path.is_file():
                path.unlink()
                arquivos_removidos.append(str(path))

    return {
        "sucesso": True,
        "erro": "",
        "backup": backup,
        "removidos": removidos,
        "arquivos_removidos": arquivos_removidos,
    }

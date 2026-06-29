from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
CHARTS_DIR = REPORTS_DIR / "charts"
PDF_DIR = REPORTS_DIR / "pdf"

CSV_FILES = {
    "pacientes": DATA_DIR / "pacientes.csv",
    "anamnese": DATA_DIR / "anamnese.csv",
    "recordatorio_habitual": DATA_DIR / "recordatorio_habitual.csv",
    "antropometria": DATA_DIR / "antropometria.csv",
    "exames": DATA_DIR / "exames.csv",
    "referencias_exames": DATA_DIR / "referencias_exames.csv",
    "alias_exames": DATA_DIR / "alias_exames.csv",
    "analise_exames": DATA_DIR / "analise_exames.csv",
    "evolucao_conduta": DATA_DIR / "evolucao_conduta.csv",
    "historico_edicoes": DATA_DIR / "historico_edicoes.csv",
}

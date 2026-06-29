from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EXAMPLE_DIR = BASE_DIR / "data_examples"

MAPA = {
    "pacientes_exemplo.csv": "pacientes.csv",
    "anamnese_exemplo.csv": "anamnese.csv",
    "recordatorio_habitual_exemplo.csv": "recordatorio_habitual.csv",
    "antropometria_exemplo.csv": "antropometria.csv",
    "exames_exemplo.csv": "exames.csv",
    "referencias_exames_exemplo.csv": "referencias_exames.csv",
    "alias_exames_exemplo.csv": "alias_exames.csv",
}

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Carregando dados de exemplo...")
    for origem, destino in MAPA.items():
        src = EXAMPLE_DIR / origem
        dst = DATA_DIR / destino
        if src.exists():
            shutil.copyfile(src, dst)
            print(f"OK: {src.name} -> {dst.name}")
        else:
            print(f"Arquivo não encontrado: {src}")

    print("\nDados de exemplo carregados.")
    print("Execute: streamlit run app_web.py")

if __name__ == "__main__":
    main()

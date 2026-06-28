import importlib.util
import platform
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REQUIRED_PACKAGES = ["pandas", "matplotlib", "streamlit"]


def check_python():
    version = sys.version_info
    ok = version.major == 3 and version.minor >= 10
    return ok, f"{version.major}.{version.minor}.{version.micro}"


def check_package(package_name):
    return importlib.util.find_spec(package_name) is not None


def main():
    print("=" * 70)
    print("NutriSoft - Verificação de Ambiente")
    print("=" * 70)
    print(f"Sistema operacional: {platform.system()} {platform.release()}")
    print(f"Pasta do projeto: {BASE_DIR}")

    python_ok, python_version = check_python()
    print(f"Python: {python_version} -> {'OK' if python_ok else 'ATENÇÃO'}")

    if not python_ok:
        print("Recomendado: Python 3.10 ou superior.")

    print("\nPacotes Python:")
    missing = []
    for package in REQUIRED_PACKAGES:
        ok = check_package(package)
        print(f"- {package}: {'OK' if ok else 'NÃO INSTALADO'}")
        if not ok:
            missing.append(package)

    data_dir = BASE_DIR / "data"
    print(f"\nPasta data/: {'OK' if data_dir.exists() else 'NÃO ENCONTRADA'}")

    app_web = BASE_DIR / "app_web.py"
    print(f"app_web.py: {'OK' if app_web.exists() else 'NÃO ENCONTRADO'}")

    print("\nResultado:")
    if python_ok and not missing and data_dir.exists() and app_web.exists():
        print("Ambiente pronto para executar o NutriSoft.")
        print("Execute: streamlit run app_web.py")
    else:
        print("Ambiente precisa de ajustes.")
        print("Execute o instalador:")
        print("- Linux: scripts/install_linux.sh")
        print("- Windows: scripts\\install_windows.bat")


if __name__ == "__main__":
    main()
